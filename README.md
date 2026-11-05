# CAFM-DTA

Condition-Aware Feature Modulation for Drug–Target Affinity prediction, extending the
PSICHIC backbone with assay-conditioned feature-wise linear modulation (FiLM). This
repository accompanies the manuscript "CAFM-DTA: Condition-Aware Feature Modulation
Disambiguates Assay Labels in Drug-Target Affinity Prediction".

## Release notes

This release restores the `simple_concat` option, fixes measurement-level prediction
export, and synchronizes Figures 6/S2 with existing-checkpoint evaluations. No new
experiments were run for this release. See [known limitations](docs/KNOWN_LIMITATIONS.md)
and [changes](docs/REVISION_NOTES.md).

## Contents and data access

- `models/`, `utils/`, `main.py`: research model and training source.
- `evaluate_checkpoint.py`: evaluate KRAS/DS2 saved checkpoints without training.
- `results/`: results plus corrected checkpoint summaries and provenance.
- `publication_figures/`: publication exports, plotting inputs and generators.
- `analysis/`: analysis entry points; Figures 6/S2 delegate to corrected code.
- `scripts/`: split-building code.

Large datasets, graph caches, predictions and checkpoints are archived on Zenodo:
https://doi.org/10.5281/zenodo.23343132. This GitHub repository contains the code, configurations,
analysis scripts and figure-generation resources. See the
[archive layout](docs/DATA_AND_ARCHIVE_README.md).

## Installation

`environment.yml` and `requirements_frozen.txt` record the environment used in the
reported work (Linux, CUDA-enabled PyTorch). Compatibility with other hardware or
runtime images is not guaranteed; run a small diagnostic before a full run.

For figure generation only:

```bash
python -m pip install -r publication_figures/requirements.txt
python publication_figures/prepare_data.py
python publication_figures/generate_corrected_figures.py
```

The last command regenerates Figures 6/S2. To generate all publication figures:
`python publication_figures/generate_figures.py`.

## Checkpoint evaluation

Download the full release from Zenodo first (three zip files, part1_of_3 to part3_of_3; extract all three into the same folder to obtain CAFM-DTA_RELEASE). Its root must contain
`07_Reproducibility/` and `08_Audit_Evidence/`. Use an absolute path:

```bash
python -B evaluate_checkpoint.py --release-root /path/to/CAFM-DTA_RELEASE --dataset kras --mode film --seed 1 --preflight
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
| Linear concatenation control | `--condition_mode simple_concat` |
| CAFM-DTA | `--condition_mode film` |

`main.py` is the research training entry point, not the checkpoint evaluation command.
It reads train.csv, valid.csv and test.csv from `--datafolder`. Use the study-specific
configuration, preprocessing caches, task flags and epoch budgets described in the
manuscript; default arguments alone do not reproduce the study. The reported results
come from the archived runs, and this GitHub copy has not been re-run end to end.

## Interpretation and reproducibility

Figure 4 parameters come from the archived cold-ligand FiLM run
`CRC_COLD_FILM_converge`, seed 1, assay format B, not the primary five-epoch model.
A small signed beta mean does not prove negligible individual shifts or establish
that multiplication is responsible for the gain.

Figures 6/S2 use corrected checkpoint evaluations; primary metrics remain unchanged.
The scientific scope and open evidence gaps are detailed in
[KNOWN_LIMITATIONS.md](docs/KNOWN_LIMITATIONS.md).

## Attribution

This is a modified PSICHIC codebase, redistributed under Apache License 2.0.
See LICENSE, NOTICE and README_PSICHIC.md. Please cite the original PSICHIC work
(Koh et al., *Nature Machine Intelligence*, 2024) and the CAFM-DTA manuscript.
