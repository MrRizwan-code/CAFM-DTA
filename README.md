# CAFM-DTA

Condition-Aware Feature Modulation for Drug–Target Affinity prediction, extending the
PSICHIC backbone with assay-conditioned FiLM. This repository supports a manuscript
being prepared for submission; acceptance or submission is not claimed.

## Revision status

This revision restores the recovered `simple_concat` option, fixes measurement-level
prediction export, and synchronizes Figures 6/S2 with existing-checkpoint evaluations.
No new experiment was performed for this repository update. The original IC50-only
numerical result remains unverified; its rerun is pending. See
[known limitations](docs/KNOWN_LIMITATIONS.md) and [changes](docs/REVISION_NOTES.md).

## Contents and data access

- `models/`, `utils/`, `main.py`: research model and training source.
- `evaluate_checkpoint.py`: evaluate KRAS/DS2 saved checkpoints without training.
- `results/`: historical results plus corrected checkpoint summaries/provenance.
- `publication_figures/`: publication exports, plotting inputs and generators.
- `analysis/`: legacy analysis entry points; Figures 6/S2 delegate to corrected code.
- `scripts/`: historical split-building code.

Large datasets, graph caches, predictions and checkpoints are **not included in this
GitHub snapshot**. They belong in the accompanying full release. The Zenodo deposit
is not yet public, and no public DOI or reviewer-access link is supplied here.
See [archive layout](docs/DATA_AND_ARCHIVE_README.md).

## Installation

`environment.yml` and `requirements_frozen.txt` preserve historical runtime records.
They are not a promise of compatibility with every rental GPU or image. The reported
work used Linux and a CUDA-enabled PyTorch environment. Confirm hardware/runtime
compatibility and run a small diagnostic before a paid full run.

For figure generation only:

```bash
python -m pip install -r publication_figures/requirements.txt
python publication_figures/prepare_data.py
python publication_figures/generate_corrected_figures.py
```

The last command regenerates Figures 6/S2. To generate all publication figures:
`python publication_figures/generate_figures.py`.

## Checkpoint evaluation

Obtain and extract the matching full release first. Its root must contain
`07_Reproducibility/` and `08_Audit_Evidence/`. Use an absolute path:

```bash
python -B evaluate_checkpoint.py --release-root /path/to/CAFM-DTA_JCIM_FINAL_RELEASE --dataset kras --mode film --seed 1 --preflight
```

After preflight succeeds, omit `--preflight` to evaluate. KRAS supports seed 1;
DS2 supports seeds 1–3; both support `off` and `film`. For DS2, provide
`--cache-dir /path/to/matching/ds2/cache` if the caches are outside the split folder.
The root must be writable because outputs go into a new timestamped evaluation
folder within it; inputs are read only. No model is trained by this tool.

## Training and condition modes

| Study arm | Argument |
|---|---|
| Unconditioned PSICHIC backbone | `--condition_mode off` |
| Nonlinear concatenation | `--condition_mode concat` |
| Recovered linear concatenation control | `--condition_mode simple_concat` |
| CAFM-DTA | `--condition_mode film` |

`main.py` is the historical research training entry point, not the checkpoint
evaluation command. It reads train.csv, valid.csv and test.csv from `--datafolder`.
Use the study-specific configuration, preprocessing caches, task flags and epoch
budget; default arguments alone are not a replication protocol. End-to-end training
from this GitHub staging copy has not been run. The separate IC50 rerun package is
not included here and must not be confused with a completed experimental result.

## Interpretation and reproducibility

Figure 4 parameters come from the archived cold-ligand FiLM run
`CRC_COLD_FILM_converge`, seed 1, assay format B, not the primary five-epoch model.
A small signed beta mean does not prove negligible individual shifts or establish
that multiplication is responsible for the gain.

Figures 6/S2 use corrected checkpoint evaluations; primary metrics remain unchanged.
The scientific scope and unresolved evidence gaps are detailed in
[KNOWN_LIMITATIONS.md](docs/KNOWN_LIMITATIONS.md).

## Attribution

This is a modified PSICHIC codebase, redistributed under Apache License 2.0.
See LICENSE, NOTICE and README_PSICHIC.md. Please cite the original PSICHIC work
when using this code. A CAFM-DTA publication citation will be added when available.
