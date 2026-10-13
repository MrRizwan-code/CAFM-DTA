# CAFM-DTA results consolidation — 8 October 2026

No training launched. simple_concat remains a single-seed supplementary control. Seeds 2/3 are not planned. Original study files were not changed.

## Primary split: five-epoch budget

| Model | Seeds | Pearson | RMSE | MAE | Spearman |
|---|---|---|---|---|---|
| OFF | 3 | 0.7893 ± 0.0052 | 0.8159 ± 0.0081 | 0.6256 ± 0.0103 | 0.7871 ± 0.0055 |
| FILM | 3 | 0.8138 ± 0.0060 | 0.7822 ± 0.0157 | 0.6010 ± 0.0134 | 0.8122 ± 0.0064 |
| simple_concat | 1 | 0.7696 | 0.8461 | 0.6538 | 0.7677 |

Recomputed from corrected evaluation-path files for OFF/FiLM and the downloaded backup for simple_concat. SD is sample SD across seeds (ddof=1). No new inference performed.

## Cold-ligand: 15 epochs, seed 1

| Model | Pearson | RMSE | MAE | Spearman |
|---|---|---|---|---|
| FILM | 0.7622 | 0.8695 | 0.6475 | 0.7577 |
| OFF | 0.7278 | 0.9184 | 0.6915 | 0.7229 |

## Evidence gap: CONCAT

Seed 3 was recalculated from its backup. Seed 2 has exact metrics recorded in the prior handoff but its prediction file was not located during this pass. Seed 1 has an older prediction export affected by the previously documented exporter issue; diagnostic metrics are retained in the JSON, excluded from the main table. The reported three-seed CONCAT summary remains provisional (Pearson approximately 0.8000 ± 0.0041; RMSE approximately 0.8089 ± 0.0069). Recover/reconcile existing evidence before publishing exact aggregate values.

## Manuscript update checklist

- Select checkpoints by lowest validation RMSE, not highest validation Pearson. The inspected trainer compares metrics rounded to four decimals. simple_concat seed 1 retains epoch 4 under this rule.
- Describe simple_concat as shared nonlinear assay-condition encoding followed by concatenation and a linear 464-to-400 projection. The fusion step has no extra ReLU or LayerNorm; CONCAT includes both.
- Clearly separate three-seed main results from single-seed simple_concat and cold-ligand results. Do not claim significance or reproducibility for single-seed differences.
- Update the cold-ligand section with the corrected row-aligned FiLM evaluation and matched 15-epoch OFF result.
- Reconcile CONCAT seed 1 and locate seed-2 predictions before finalizing its statistics.
- Update architecture labels, captions, Methods, Results, abstract and limitations consistently with the verified evidence.
- Keep cleaned-data sensitivity optional. The separate simple assay-aware baseline in the older handoff remains a scope question; do not silently equate it to simple_concat.

## Next step

Recover/reconcile CONCAT evidence already generated; do not start new training. After that, update a separate manuscript working copy. Full paths and unrounded metrics are in verified_metrics.json.
