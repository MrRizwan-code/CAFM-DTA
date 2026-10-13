# CAFM-DTA ? evidence and limitations

## CONCAT seed-1 prediction export

The historical CONCAT seed-1 test_prediction_seed1.csv is unreliable for measurement-level evaluation of repeated protein?ligand pairs. The original export matched on protein and ligand without preserving assay-condition distinctions, overwriting condition-specific predictions.

The affected seed-1 test slice contains 2,432 multi-assay pairs with 5,029 measurements. The archived CSV-derived Pearson correlation differs from the reported training-log metric. The training log reports approximately 0.8028 Pearson, rounded to four decimals; the corrupted CSV gives approximately 0.78888.

Do not treat that CSV as a validated evaluation-path prediction file, infer exact seed-1 CONCAT metrics from it, or report a high-precision three-seed CONCAT aggregate based on that rounded log.

## Primary OFF/FILM evidence

Use the six separate EVALPATH primary test prediction files for OFF/FILM analyses. Historical screening-path run CSVs are preserved for audit rather than substituted for these files.

## Figure 3B confidence intervals

Seed-1 Pearson gains are assessed with 5,000 pair-clustered bootstrap resamples, sampling protein?ligand pairs together with their measurements within each slice.

Corrected 95% intervals:
All measurements: [0.018800, 0.026363].
Multi-assay measurements: [0.061088, 0.084144].
Single-assay measurements: [0.007516, 0.015622].

These quantify within-test-set sampling uncertainty at seed 1, not variation across independently trained seeds. The older measurement-level bootstrap data file is historical and not authoritative for the corrected figure.

## Cold-ligand experiment provenance

The original archive README refers to a two-epoch cold-ligand OFF reference and separate FiLM runs. Newer 15-epoch cold-ligand OFF artifacts and row-aligned evaluations are also included as additional evidence. Do not conflate these experiments or their training budgets.

## Other caveats

Source code preserves the original prediction-export implementation. It should not be represented as a corrected exporter until separately fixed and validated.

Figures and reported metrics should retain their original methodological qualifications. Different datasets, seeds, checkpoints, and evaluation paths are not necessarily interchangeable.

The source archive identifies ChEMBL release 37 and CC BY-SA 3.0. Confirm applicable data redistribution obligations and license compatibility before making the bundled split files public.

Archived references and prior documentation may contain superseded statements. The corrected manuscript, pair-clustered bootstrap evidence, and this limitations record take precedence for the identified corrections.

A final scientific consistency review, end-to-end reproduction check, and public-release permission review remain outstanding.
