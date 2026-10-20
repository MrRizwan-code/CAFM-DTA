"""Evaluate an existing KRAS/DS2 checkpoint without training or overwriting archives.

Start with --preflight. Graph caches are read, never created or modified.
The entire working release can be moved to its original Linux model environment.
"""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import hashlib
import importlib.util
import json
import math
import re
import time
import uuid


CODE = Path(__file__).resolve().parent
ROOT = CODE
MODULES = ['torch', 'torch_geometric', 'torch_scatter', 'torch_sparse',
           'numpy', 'pandas', 'scipy', 'lifelines', 'rdkit', 'tqdm',
           'sklearn', 'esm', 'reprint']


def sha256(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def select_log_reference(path):
    blocks = re.split(r'Epoch:\s*(\d+)\s*-\s*Model Results', path.read_text(encoding='utf-8-sig'))
    candidates = []
    for index in range(1, len(blocks), 2):
        validation = re.search(r'Validation Results:\s*(\{.*?\})', blocks[index + 1], re.S)
        test = re.search(r'Test Results:\s*(\{.*?\})', blocks[index + 1], re.S)
        if validation and test:
            candidates.append({'epoch': int(blocks[index]),
                               'validation': json.loads(validation[1]),
                               'test': json.loads(test[1])})
    if not candidates:
        raise ValueError('No validation/test reference found in ' + str(path))
    selected = min(candidates, key=lambda item: item['validation']['rmse'])
    selected['qualification'] = 'Selected from the historical log, not independently read from checkpoint metadata.'
    return selected


def input_paths(dataset, mode, seed, cache_dir):
    if dataset == 'kras' and seed != 1:
        raise ValueError('Only seed 1 is archived for KRAS; this script does not train new seeds.')
    archive = ROOT / '08_Audit_Evidence/archived_runs'
    if dataset == 'kras':
        folder = archive / 'CRC_UNSEEN' / ('CRC_UNSEEN_' + mode.upper())
        split = ROOT / '07_Reproducibility/data_splits/kras_unseen'
    else:
        folder = archive / 'ds2_allseeds_15ep' / f'DS2_{mode.upper()}_SEED{seed}_15EP'
        split = ROOT / '07_Reproducibility/data_splits/ds2'
    recovered_cache = ROOT / '07_Reproducibility/graph_caches/primary_recovered'
    cache = (Path(cache_dir).expanduser().resolve() if cache_dir else
             recovered_cache if dataset == 'kras' and recovered_cache.is_dir() else split)
    saved = folder / f'save_model_seed{seed}'
    return {
        'test_csv': split / 'test.csv', 'checkpoint': saved / 'model.pt',
        'configuration': saved / 'config.json', 'degrees': saved / 'degree.pt',
        'condition_maps': folder / 'condition_maps.json',
        'training_log': folder / f'full_result-{seed}.txt',
        'protein_cache': cache / 'protein.pt', 'ligand_cache': cache / 'ligand.pt',
        'exporter_source': CODE / 'utils/utils.py',
        'condition_encoder_source': CODE / 'models/condition_encoder.py',
        'model_source': CODE / 'models/net.py',
        'dataset_source': CODE / 'utils/dataset.py',
        'condition_map_source': CODE / 'utils/condition_map.py',
    }


def validate_condition_maps(maps):
    expected = {
        'std_map': {'IC50': 0, 'Ki': 1, 'EC50': 2, 'Kd': 3, 'other': 4},
        'assay_map': {'B': 0, 'F': 1, 'other': 2},
    }
    if maps != expected:
        raise ValueError('Saved condition maps differ from the archived model vocabulary.')


def preflight(args):
    paths = input_paths(args.dataset, args.mode, args.seed, args.cache_dir)
    missing_inputs = [name for name, path in paths.items() if not path.is_file()]
    missing_modules = [name for name in MODULES if importlib.util.find_spec(name) is None]
    configuration_valid = False
    maps_valid = False
    if paths['configuration'].is_file():
        config = json.loads(paths['configuration'].read_text(encoding='utf-8-sig'))
        if not isinstance(config.get('params'), dict) or not config.get('tasks', {}).get('regression_task'):
            raise ValueError('A saved regression configuration with nested params is required.')
        configuration_valid = True
    if paths['condition_maps'].is_file():
        validate_condition_maps(json.loads(paths['condition_maps'].read_text(encoding='utf-8-sig')))
        maps_valid = True
    return paths, {
        'dataset': args.dataset, 'mode': args.mode, 'seed': args.seed,
        'ready': not missing_inputs and not missing_modules,
        'missing_inputs': missing_inputs, 'missing_runtime_modules': missing_modules,
        'configuration_valid': configuration_valid, 'condition_maps_valid': maps_valid,
        'paths': {key: str(value) for key, value in paths.items()},
        'preflight_only': args.preflight,
        'training': 'disabled; no optimizer or training code is used',
        'output_policy': 'New timestamped evaluation folder inside this working release only.',
    }


def finite_or_none(value):
    result = float(value)
    return result if math.isfinite(result) else None


def calculate_metrics(y, prediction):
    import numpy as np
    from scipy.stats import pearsonr, spearmanr
    from lifelines.utils import concordance_index
    y, prediction = np.asarray(y, dtype=float), np.asarray(prediction, dtype=float)
    if len(y) == 0:
        return {'n': 0}
    variable = len(y) > 1 and np.ptp(y) > 0 and np.ptp(prediction) > 0
    return {
        'n': len(y), 'pearson': finite_or_none(pearsonr(y, prediction)[0]) if variable else None,
        'spearman': finite_or_none(spearmanr(y, prediction)[0]) if variable else None,
        'rmse': float(np.sqrt(np.mean((prediction - y) ** 2))),
        'mae': float(np.mean(np.abs(prediction - y))),
        'bias': float(np.mean(prediction - y)),
        'ci': finite_or_none(concordance_index(y, prediction)) if len(y) > 1 and np.ptp(y) > 0 else None,
    }


def evaluate(args, paths, inspection):
    import inspect
    import platform
    import random
    import numpy as np
    import pandas as pd
    import torch
    import torch_geometric
    from torch_geometric.loader import DataLoader
    from models.net import net
    from utils.dataset import ProteinMoleculeDataset
    from utils.condition_map import apply_condition_map
    from utils.utils import virtual_screening

    if args.device.startswith('cuda') and not torch.cuda.is_available():
        raise RuntimeError('CUDA is unavailable. Use the model environment or explicitly choose --device cpu.')
    torch.set_num_threads(args.cpu_threads)
    random.seed(args.seed)
    np.random.seed(args.seed)
    torch.manual_seed(args.seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(args.seed)

    # Hash inputs before evaluation; no input is ever saved back to these paths.
    hashes = {name: sha256(path) for name, path in paths.items()}
    df = pd.read_csv(paths['test_csv']).reset_index(drop=True)
    full_test_rows = len(df)
    if args.probe_rows:
        df = df.iloc[:args.probe_rows].copy().reset_index(drop=True)
    is_probe = bool(args.probe_rows)
    required = ['Protein', 'Ligand', 'regression_label', 'standard_type', 'assay_type']
    if any(name not in df for name in required):
        raise ValueError('Test data lacks required label, identity or condition columns.')
    if 'source_row' in df:
        if not np.array_equal(df.source_row.to_numpy(), np.arange(len(df))):
            raise ValueError('Existing source_row column is not aligned.')
    else:
        df.insert(0, 'source_row', np.arange(len(df)))
    maps = json.loads(paths['condition_maps'].read_text(encoding='utf-8-sig'))
    validate_condition_maps(maps)
    standard, assay = apply_condition_map(df, maps['std_map'], maps['assay_map'])
    df['cond_std'], df['cond_assay'] = standard, assay

    # Graph objects are trusted local research caches. Do not use untrusted cache files.
    protein = torch.load(paths['protein_cache'], map_location='cpu', weights_only=False)
    ligand = torch.load(paths['ligand_cache'], map_location='cpu', weights_only=False)
    missing_protein = set(df.Protein) - set(protein)
    missing_ligand = set(df.Ligand) - set(ligand)
    if missing_protein or missing_ligand:
        raise ValueError(f'Cache coverage incomplete: {len(missing_protein)} proteins, {len(missing_ligand)} ligands missing.')
    dataset = ProteinMoleculeDataset(df, ligand, protein, device='cpu')
    loader = DataLoader(dataset, batch_size=args.batch_size, shuffle=False, drop_last=False,
                        num_workers=0, follow_batch=['mol_x', 'clique_x', 'prot_node_aa'])
    config = json.loads(paths['configuration'].read_text(encoding='utf-8-sig'))
    params = dict(config['params'])
    allowed = set(inspect.signature(net.__init__).parameters)
    if set(params) - allowed:
        raise ValueError('Unsupported saved model parameters: ' + ', '.join(sorted(set(params) - allowed)))
    degrees = torch.load(paths['degrees'], map_location='cpu', weights_only=True)
    model = net(degrees['ligand_deg'], degrees['protein_deg'], **params,
                regression_head=True, classification_head=False, multiclassification_head=0,
                condition_mode=args.mode, num_std=len(maps['std_map']),
                num_assay=len(maps['assay_map']), device=args.device)
    expected_count = {'off': 5871321, 'film': 5931897}[args.mode]
    count = sum(parameter.numel() for parameter in model.parameters())
    if count != expected_count:
        raise ValueError(f'Model parameter mismatch: {count} versus expected {expected_count}.')
    model.load_state_dict(torch.load(paths['checkpoint'], map_location='cpu', weights_only=True), strict=True)
    model = model.to(args.device).eval()

    # The corrected export function validates order/conditions and runs no_grad.
    inference_started = time.perf_counter()
    out = virtual_screening(df, model, loader, result_path='', save_interpret=False,
                            ligand_dict=ligand, device=args.device)
    inference_seconds = time.perf_counter() - inference_started
    pd.testing.assert_frame_equal(out[df.columns], df)
    prediction = out.predicted_binding_affinity.to_numpy(float)
    y = out.regression_label.to_numpy(float)
    if len(out) != len(df) or not np.isfinite(prediction).all() or not np.isfinite(y).all():
        raise ValueError('Output row count or finite-value verification failed.')
    overall = calculate_metrics(y, prediction)
    multi = out.duplicated(['Protein', 'Ligand'], keep=False).to_numpy()
    slices = {
        'multi_assay': calculate_metrics(y[multi], prediction[multi]),
        'single_assay': calculate_metrics(y[~multi], prediction[~multi]),
    }
    per_type = {str(key): calculate_metrics(group.regression_label, group.predicted_binding_affinity)
                for key, group in out.groupby('standard_type', dropna=False)}
    per_target = ({str(key): calculate_metrics(group.regression_label, group.predicted_binding_affinity)
                   for key, group in out.groupby('target_name', dropna=False)}
                  if 'target_name' in out else {})
    reference = select_log_reference(paths['training_log'])
    comparison = {}
    if not is_probe:
        for metric in ['pearson', 'rmse']:
            delta = overall[metric] - reference['test'][metric]
            comparison[metric] = {'regenerated_minus_logged': delta,
                                  'tolerance': args.log_tolerance,
                                  'within_tolerance': abs(delta) <= args.log_tolerance}
    matches = all(item['within_tolerance'] for item in comparison.values()) if not is_probe else None
    output_root = ROOT / '04_Evaluation_Predictions' / (
        'checkpoint_probes' if is_probe else 'corrected_checkpoint_evaluations')
    run_name = (f'{args.dataset}_{args.mode}_seed{args.seed}_'
                + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ_') + uuid.uuid4().hex[:8])
    output = output_root / run_name
    if ROOT.resolve() not in output.resolve().parents:
        raise ValueError('Output path must remain inside this release.')
    output.mkdir(parents=True, exist_ok=False)
    csv = output / 'test_predictions_aligned.csv'
    out.to_csv(csv, index=False, mode='x')
    report = {
        'dataset': args.dataset, 'mode': args.mode, 'seed': args.seed,
        'probe_only': is_probe, 'full_test_rows': full_test_rows,
        'training_performed': False, 'parameter_count': count,
        'paths': inspection['paths'], 'input_sha256': hashes,
        'output_csv': str(csv.relative_to(ROOT)), 'output_csv_sha256': sha256(csv),
        'overall': overall, 'slices': slices, 'per_standard_type': per_type,
        'per_target': per_target, 'historical_log_reference': reference,
        'comparison_with_rounded_log': comparison,
        'requires_review': not matches if not is_probe else True,
        'inference_seconds': inference_seconds,
        'measurements_per_second': len(out) / inference_seconds,
        'environment': {'python': platform.python_version(), 'platform': platform.platform(),
                        'torch': str(torch.__version__), 'torch_geometric': str(torch_geometric.__version__),
                        'device': args.device, 'cpu_threads': args.cpu_threads},
        'qualification': ('Partial runtime probe; not a full-set scientific result.' if is_probe else
                          'Reported checkpoint inference only. No new seed, checkpoint selection or training.'),
    }
    with (output / 'metrics_and_provenance.json').open('x', encoding='utf-8') as stream:
        json.dump(report, stream, indent=2, allow_nan=False)
    print(json.dumps({'output_folder': str(output), 'metrics': overall,
                      'probe_only': is_probe, 'inference_seconds': inference_seconds,
                      'matches_rounded_log': matches, 'training_performed': False}, indent=2))
    return 0 if is_probe or matches else 2


def main(argv=None):
    global ROOT
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--release-root', required=True, help='Extracted full release containing 07_Reproducibility and 08_Audit_Evidence.')
    parser.add_argument('--dataset', choices=['kras', 'ds2'], required=True)
    parser.add_argument('--mode', choices=['off', 'film'], required=True)
    parser.add_argument('--seed', type=int, choices=[1, 2, 3], default=1)
    parser.add_argument('--cache-dir', help='Read-only folder containing original protein.pt and ligand.pt.')
    parser.add_argument('--device', default='cuda:0')
    parser.add_argument('--batch-size', type=int, default=16)
    parser.add_argument('--cpu-threads', type=int, default=4)
    parser.add_argument('--probe-rows', type=int, default=0,
                        help='Optional partial runtime test. Outputs are separate from full evaluations.')
    parser.add_argument('--log-tolerance', type=float, default=0.0001)
    parser.add_argument('--preflight', action='store_true', help='Inspect inputs/runtime only; no model loading or outputs.')
    args = parser.parse_args(argv)
    ROOT = Path(args.release_root).expanduser().resolve()
    if args.batch_size <= 0 or args.cpu_threads <= 0 or args.probe_rows < 0 or args.log_tolerance < 0:
        parser.error('Batch size/threads must be positive; probe rows/tolerance must be nonnegative.')
    paths, inspection = preflight(args)
    if args.preflight or not inspection['ready']:
        print(json.dumps(inspection, indent=2))
        return 0 if inspection['ready'] else 2
    return evaluate(args, paths, inspection)


if __name__ == '__main__':
    raise SystemExit(main())
