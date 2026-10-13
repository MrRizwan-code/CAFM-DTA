# CAFM-DTA

Condition-Aware Feature Modulation for Drug-Target Affinity prediction.

CAFM-DTA extends the PSICHIC backbone with a feature-wise linear modulation
(FiLM) branch. The branch maps two assay descriptors - measurement type and
assay format - onto a per-feature scale vector gamma and shift vector beta that
transform the 400-dimensional protein-ligand interaction representation:

    h' = gamma * h + beta

The branch is initialized at identity (gamma = 1, beta = 0), so disabling it
reproduces the unconditioned backbone exactly. The two arms therefore differ
only in the condition pathway.

This repository accompanies a manuscript submitted to the *Journal of Chemical
Information and Modeling*.

---

## 1. Relationship to PSICHIC

This is a modified copy of the PSICHIC codebase
(https://github.com/huankoh/PSICHIC), redistributed under the Apache License
2.0. See `LICENSE` for the license text and `NOTICE` for the list of files
modified and added. PSICHIC's original README is kept as `README_PSICHIC.md`.

The condition branch lives in two new files:

| File | What it does |
|---|---|
| `models/condition_encoder.py` | The FiLM branch: maps the condition code to gamma and beta |
| `utils/condition_map.py` | Maps measurement type and assay format to integer condition codes |

and is wired into five modified files: `main.py`, `models/net.py`,
`utils/dataset.py`, `utils/trainer.py`, `utils/utils.py`.

**Naming.** Code identifiers keep PSICHIC's original names; the model is
selected by one argument. The three arms in the manuscript map as follows:

| Manuscript | Code |
|---|---|
| CAFM-DTA | `--condition_mode film` |
| Concatenation control | `--condition_mode concat` |
| Unconditioned PSICHIC backbone (baseline) | `--condition_mode off` |

---

## 2. Installation

~~~bash
conda env create -f environment.yml
conda activate cafm-dta
~~~

`environment.yml` pins the exact versions used for all reported runs (Python
3.12.3, PyTorch 2.8.0 with CUDA 12.8, PyTorch Geometric 2.8.0, and every other
package the code imports). It targets Linux with an NVIDIA GPU, the platform
the models were trained on. `requirements_frozen.txt` records the complete
package list of the training machine for reference; it is not meant to be
installed directly. PSICHIC's original environment files are not included.

---

## 3. Running the model

`main.py` reads `train.csv`, `valid.csv` and `test.csv` from the folder given
by `--datafolder`. Each folder under `data/splits/` is laid out this way.
Conditioning is controlled by a single argument; everything else is identical
between the two arms.

~~~bash
# unconditioned baseline
python main.py --datafolder data/splits/primary --result_path runs/primary_off_seed1 \
    --condition_mode off --regression_task True --seed 1

# CAFM-DTA
python main.py --datafolder data/splits/primary --result_path runs/primary_film_seed1 \
    --condition_mode film --regression_task True --seed 1
~~~

Featurization caches (`protein.pt`, `ligand.pt`) are built automatically on
the first run in each datafolder and saved there; later runs load them.
Building the protein cache uses the ESM-2 model `esm2_t33_650M_UR50D`, which
the `fair-esm` package downloads on first use (internet access required,
roughly 2.5 GB). Each cache holds only the proteins and ligands of its own
datafolder, and an existing cache is loaded without being checked, so delete
`protein.pt` and `ligand.pt` after changing any CSV file. PNA degree
statistics (`degree.pt`) are computed from the training data when absent.
Epoch budgets for each experiment are given in the manuscript Methods.

---

## 4. Data

Affinity measurements derive from ChEMBL release 37
(CC BY-SA 3.0), retrieved through the ChEMBL web services.

| Split | Folder | Train / valid / test rows | In this repo |
|---|---|---|---|
| Primary (5 CRC targets, random) | `data/splits/primary/` | 229,480 / 28,683 / 28,673 | valid, test |
| KRAS unseen target | `data/splits/kras_unseen/` | 210,124 / 23,364 / 53,348 | valid, test |
| Cold ligand | `data/splits/cold/` | 229,289 / 28,849 / 28,698 | valid, test |
| Second dataset (DS2) | `data/splits/ds2/` | 15,486 / 1,935 / 1,937 | train, valid, test |

Primary targets: EGFR, BRAF, PIK3CA, KRAS, mTOR. DS2 targets: ERBB2, MAP2K1,
AKT1, CDK4, SRC.

**Archived on Zenodo** (too large for GitHub). The archive mirrors the
`data/splits/` layout, so each file drops into place under its own name:

| Item | Goes in |
|---|---|
| Primary, KRAS-unseen and cold-ligand `train.csv` | `data/splits/<split>/` |
| IC50-only control split | `data/splits/ic50only/` |
| Label-offset intervention datasets (4 offsets) | `data/splits/kip00/`, `kip05/`, `kip10/`, `kip20/` |
| Trained model weights, all reported runs | `runs/` |

Zenodo DOI: `[TO BE ADDED]`

### Rebuilding the splits

- **Primary and KRAS unseen:** `scripts/dataset_split.ipynb`, the original
  split notebook.
- **Cold ligand:** `scripts/make_cold_split.py` rebuilds it from the primary
  split. It shuffles unique ligands with a fixed seed (42) and assigns them
  80/10/10, so no ligand appears in more than one split. Verified to reproduce
  the published split row for row.

  ~~~bash
  python scripts/make_cold_split.py --primary_dir data/splits/primary --out_dir data/splits/cold
  ~~~

- **DS2:** all three files are included directly.

---

## 5. What is in this repository

| Path | Contents |
|---|---|
| `main.py` | Training and evaluation entry point |
| `environment.yml`, `requirements_frozen.txt` | Pinned environment; full package record of the training machine |
| `models/` | Network, FiLM condition branch, PSICHIC layers |
| `utils/` | Data handling, trainer, condition map, metrics |
| `data/splits/` | Train/validation/test splits (see section 4) |
| `scripts/` | Split-building code |
| `analysis/` | Scripts that produce the reported figures and tables |
| `logs/` | Training logs from the reported runs |
| `results/` | Frozen metric JSONs and per-run outputs (including `results/ds2/`) |
| `examples/`, `selectivity/`, `PSICHIC-prod/`, `image/`, `screening.py`, `PSICHIC.ipynb` | Unmodified PSICHIC material |
| `trained_weights/` | PSICHIC's own pretrained model folders; the `.pt` files are not redistributed here, get them from upstream PSICHIC |

---

## 6. Mapping from paper to code

Each figure panel and supplementary figure is produced by one script in `analysis/`. Each script's header lists its inputs, how to run it, and where its PDF (vector) and PNG (600 dpi) are saved. `fig3b_bootstrap_CI.py` takes the two primary-split prediction files as arguments (see its header). The three Figure 3 panels are produced separately and assembled into one figure.

| Paper item | Script | Content |
|---|---|---|
| Figure 1 | `analysis/fig1_architecture.py` | Architecture schematic |
| Figure 2 | `analysis/fig2_primary_ablation.py` | off / concat / film ablation, primary split |
| Figure 3a | `analysis/fig3a_multi_vs_single.py` | Accuracy by pair type (its second panel is superseded by Figure 3b) |
| Figure 3b | `analysis/fig3b_bootstrap_CI.py` | Per-slice gain with 95% bootstrap CIs (also prints the Figure S1 CIs) |
| Figure 3c | `analysis/fig3c_error_vs_disagreement.py` | Error reduction vs measurement disagreement |
| Figure 4 | `analysis/fig4_gamma_beta_interpretability.py` | FiLM gamma/beta read-out |
| Figure 5 | `analysis/fig5_intervention.py` | Ki label-offset intervention |
| Figure 6 | `analysis/fig6_ds2_radar.py` | Replication on the second dataset (DS2) |
| Figure 7 | `analysis/fig7_coldsplit_leaderboard.py` | Cold-ligand split leaderboard |
| Figure S1 | `analysis/figS1_perassay_gain.py` | Gain per measurement type |
| Figure S2 | `analysis/figS2_pertarget_gain.py` | Per-target gain, ten targets |
| Figure S3 | `analysis/figS3_applicability_domain.py` | Applicability domain |
| Figure S4 | `analysis/figS4_calibration.py` | Calibration |
| Tables 1-4 | none | Values taken from the frozen result files in `results/` |

---

## 7. Determinism

Each run seeds NumPy, PyTorch (CPU and CUDA), Python's `random`, and
`PYTHONHASHSEED` from one seed argument. Exact bitwise reproducibility on GPU
is not guaranteed, because some graph scatter operations are nondeterministic.

---

## 8. Citation

~~~
[BibTeX to be added on acceptance]
~~~

If you use this code, please also cite PSICHIC.
