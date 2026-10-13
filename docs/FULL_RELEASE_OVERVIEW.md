# CAFM-DTA ? JCIM reproducibility release candidate

CAFM-DTA (Condition-Aware Feature Modulation for Drug?Target Affinity) extends the PSICHIC drug?protein graph backbone with an assay-condition branch applying FiLM to the interaction fingerprint.

STATUS: Locally assembled release candidate. Scientific, licensing, and final integrity review remain necessary before public deposit.

## Directory structure

- 01_Source_Code: implementation, analysis scripts, configuration, and original software notices.
- 02_Configurations: supplementary model configurations.
- 03_Experimental_Results: consolidated metrics, archived results, and corrected Figure 3B bootstrap evidence.
- 04_Evaluation_Predictions: primary OFF/FiLM evaluation-path predictions and additional evaluation artifacts.
- 05_Publication_Figures: regenerated main and supplementary figures, underlying data, and generation scripts.
- 06_Manuscript_and_SI: revised manuscript, supplementary information, and correction-preserving document versions.
- 07_Reproducibility: dataset splits, original archive documentation, and reproducibility materials.
- 08_Audit_Evidence: preserved training/run records and additional supporting evidence.

## Experimental modes

OFF: unconditioned PSICHIC backbone.
CONCAT: condition-concatenation control.
FILM: condition-aware FiLM modulation (CAFM-DTA).

## Authoritative evidence

Primary OFF/FILM test predictions: 04_Evaluation_Predictions/primary_seed1 through primary_seed3, using EVALPATH files.

Consolidated primary results: 03_Experimental_Results/verified_results.json.

Figure 3B: pair-clustered bootstrap evidence in 03_Experimental_Results/fig3b_pair_cluster_bootstrap_results.csv, corrected plotted data in 05_Publication_Figures/data/slice_bootstrap_pair_cluster.json, and regenerated figures in 05_Publication_Figures/figures/.

Revised manuscript with corrected Figure 3 embedded: 06_Manuscript_and_SI/CAFM-DTA_JCIM_Figure3_Updated.docx.

Archived run CSV files are retained as historical evidence. They are not interchangeable with evaluation-path predictions.

## Reproduction and dependencies

Consult 01_Source_Code/CAFM-DTA/README.md, environment.yml, requirements_frozen.txt, main.py, config.json, and the analysis scripts. Experiment-specific settings and checkpoints are preserved under 08_Audit_Evidence/archived_runs.

Complete end-to-end reproduction from this rearranged package has not yet been independently validated. Do not assume paths in historical scripts automatically match this release layout.

## Distribution

Large datasets and checkpoint artifacts should generally be deposited separately from GitHub source code. Data redistribution terms, dependencies, software notices, and personal or confidential metadata must be checked before publication.

See 08_Audit_Evidence/KNOWN_LIMITATIONS.md before citing or reusing results. Original research files have been preserved; this is a staged copy.
