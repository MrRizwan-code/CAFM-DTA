# Data and accompanying archive

No split CSVs, graph caches, model weights or large prediction files are in this
GitHub snapshot. Access to the accompanying private archive must be arranged with
the author. No public Zenodo DOI is asserted.

The checkpoint evaluator expects the existing full-release layout:

```
CAFM-DTA_JCIM_FINAL_RELEASE/
  07_Reproducibility/
    data_splits/kras_unseen/test.csv
    data_splits/ds2/test.csv
    graph_caches/primary_recovered/{protein.pt,ligand.pt}
  08_Audit_Evidence/archived_runs/
    CRC_UNSEEN/{CRC_UNSEEN_OFF,CRC_UNSEEN_FILM}/
    ds2_allseeds_15ep/DS2_{OFF,FILM}_SEED{1,2,3}_15EP/
```

Each run folder contains condition_maps.json, full_result-SEED.txt and a
save_model_seedSEED folder with model.pt, config.json and degree.pt.
DS2 requires its own matching graph caches, passed with --cache-dir when necessary.
Graph caches must come from trusted research files.

Corrected prediction exports belong under
04_Evaluation_Predictions/corrected_checkpoint_evaluations in the full release.
Compact reports here retain input/output hashes; FULL_RELEASE/ denotes that archive,
and AUDIT_WORKING_COPY/ denotes supporting local audit material, not a web link.

Do not claim all reported checkpoints are supplied: IC50-only original evidence is missing.
Do not substitute historical screening predictions for corrected evaluation outputs.
