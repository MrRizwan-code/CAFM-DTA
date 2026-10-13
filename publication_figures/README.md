# CAFM-DTA rebuilt figures

This folder contains main Figures 1–7, supplementary Figures S1–S4, and a separate condition-variant diagram accompanying Figure 1. Each is saved as a 600-DPI PNG, a single-page PDF, and an SVG. The PDF and SVG retain vector labels and chart elements; the dense scatter points in Figure 3 are rasterized at export resolution. The original Word documents remain unchanged. The corrected release manuscript contains the updated Figure 3.

## Regenerate in VS Code

1. Open `CAFM_figures.code-workspace` in VS Code.
2. Select a Python interpreter with the packages in `requirements.txt`.
3. Open `generate_figures.py` and choose **Run Python File**, or run `python generate_figures.py` in the terminal.

The generation script reads the bundled `data` folder. It does not need a GPU, training checkpoint or internet access. Colors, labels and layouts can be edited in that script. On the current workstation it can use the already installed plotting libraries from the neighboring manuscript revision folder. On another computer install the three packages from requirements.txt into your selected Python environment first.

`prepare_data.py` is an optional provenance script that reconstructs the per-target summary and legacy measurement-level Figure 3 bootstrap intervals (not the corrected pair-clustered intervals) from the original CFAM archive layout. It is not required for ordinary regeneration, because its outputs are bundled. It requires the original study files and does not train models.

## Data sources and precision

| Figures | Source and status |
|---|---|
| 1 and companion | Previously inspected implementation; condition embeddings 32 dimensions each, code 64, fingerprint 400, regression head 400→200→1. Dropout 0.1 follows the first condition-MLP ReLU. FiLM projections are zero-initialized. |
| 2 | verified_results.json: prediction-derived primary results. CONCAT seed 1 uses a four-decimal log, so its aggregate is approximate; simple_concat is seed 1 only. |
| 3a?b | `slice_bootstrap_pair_cluster.json`: seed-1 primary OFF/FiLM predictions; 5,000 protein?ligand pair-clustered bootstrap resamples within each slice. Supporting evidence: `fig3b_pair_cluster_bootstrap_results.csv` in `03_Experimental_Results`. The older `slice_bootstrap.json` is retained for provenance, not used for the corrected figure. |
| 3c | Archived step_error_vs_disagreement.json: 2,417 per-pair points and the reported correlation. |
| 4 | Archived filmparam_analysis.json. Its gamma_mean field represents the scale deviation g(c), not the final multiplier 1+g(c). Matrix rows/columns are reordered together. |
| 5 | Within-pair values retained from the original figure script at three decimals: 0, 0.480, 1.140, 2.054. Absolute shifts use step2_recovery_predshift.json. |
| 6 | Updated primary summaries and DS2 mean/SD values retained at the manuscript's reported precision. |
| 7 | Updated matched cold-ligand results from verified_results.json; external baseline values from their archived result JSONs. |
| S1 | Archived step12c_perassay.json; no invented uncertainty bars. |
| S2 | per_target.csv reconstructed from the archived primary slice table and DS2 screening-path predictions. The DS2 repeated-pair limitation remains; regeneration does not validate or repair the original model export. |
| S3 | Archived step12e_ad_curve.json, including all bin counts. |
| S4 | Archived step12d_calibration.json; bias mean and sample SD calculated from its recorded per-seed values. |

No new model training was performed. Archived analyses were redrawn from recorded values; only the specifically identified computations were repeated. These figures do not remove the study's existing data limitations. The table-of-contents graphic is not part of this replacement set.

## Caption alignment when inserting

- Figure 1: the optional condition-variant diagram is a separate file; insert as an accompanying panel only if desired. The architecture no longer packs the control descriptions into small footnotes.
- Figure 2: large points are means (diamond for the single-seed control), small points are individual seeds, and whiskers are sample SD. Labels at the top of each panel are the means.
- Figure 3b: 5,000 pair-clustered bootstrap resamples, with protein?ligand pairs as sampling units. Corrected 95% confidence intervals are [0.0188, 0.0264] for all measurements, [0.0611, 0.0841] for multi-assay measurements, and [0.0075, 0.0156] for single-assay measurements. These describe within-test-set uncertainty at seed 1, not between-seed variation.
- Figure 5: the plotted through-origin within-pair slope is 1.045 from the recorded three-decimal inputs; this is the same result previously rounded to 1.05.
- Figure 6: replace “bars” and “hatched bars” with **points and ±1 sample-SD whiskers**. Panel metrics and comparisons are unchanged.
- Figure 7: describe **points**, ordered off, film, DeepDTA, GraphDTA. The dashed divider separates the matched control from the contextual external baselines; no uncertainty is estimated for these single runs.
- Figures S1–S4: retain the revised supplementary caption qualifications, especially DS2 export provenance and the lowest-similarity bin.

Use the PNG files in Word at the intended figure width without stretching them. Prefer PDF or SVG for editing and vector-quality reproduction. Detailed methods belong in captions; avoid shrinking these labels to fit an overly narrow column.
