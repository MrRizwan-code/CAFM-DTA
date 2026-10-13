# CAFM-DTA - archived run artifacts

Companion archive to the CAFM-DTA code repository ([repository URL]). It holds the trained
weights, run settings, predictions and large split files for the runs reported in the paper.
Affinity data are derived from ChEMBL release 37 (CC BY-SA 3.0).

## Mode names
- off    = unconditioned PSICHIC backbone (baseline)
- concat = concatenation control
- film   = CAFM-DTA (condition-aware FiLM)

## runs\
| Folder | Split (datafolder) | Mode | Seed | Epochs |
|---|---|---|---|---|
| CRC_OFF, CRC_FILM | crc (primary) | off, film | 1 | 5 |
| CRC_CONCAT\CRC_CONCAT | crc (primary) | concat | 1 | 5 |
| CRC_seed2\CRC_OFF_seed2, CRC_FILM_seed2 | crc (primary) | off, film | 2 | 5 |
| CRC_seed3\CRC_OFF_seed3, CRC_FILM_seed3 | crc (primary) | off, film | 3 | 5 |
| CRC_UNSEEN\CRC_UNSEEN_OFF, CRC_UNSEEN_FILM | crc_unseen (KRAS-unseen) | off, film | 1 | 5 |
| CRC_COLD\CRC_COLD_OFF_seed1 | crc_coldligand | off | 1 | 2 of 5 (reference run) |
| CRC_COLD\CRC_COLD_FILM_seed1 | crc_coldligand | film | 1 | 5 |
| CRC_COLD_FILM_converge\CRC_COLD_FILM_converge | crc_coldligand | film | 1 | 15 |
| ds2_allseeds_15ep\DS2_<OFF/FILM>_SEED<1-3>_15EP | crc_dataset2 (second dataset) | off, film | 1-3 | 15 |

Files in each run folder:
- save_model_seed<N>\model.pt, config.json (model settings), degree.pt
- condition_maps.json - fitted condition maps
- model_params.txt - run settings (datafolder, condition_mode, seed, epochs)
- full_result-<N>.txt - per-epoch results
- test_prediction_seed<N>.csv - end-of-training test-set predictions (screening path)

## predictions_evalpath\
- primary_seed1, primary_seed2, primary_seed3: OFF_ and FILM_test_prediction_EVALPATH_seed<N>.csv.
  Evaluation-path test-set predictions on the primary split. All primary-split analyses in
  the paper use these files (see Methods). To run analysis\fig3b_bootstrap_CI.py, place the
  two seed-1 files next to the script.
- label_offset: evalpath_preds_STEP2_KIP00/05/10/20.npy - test-set predictions of the
  label-offset control runs, one file per setting, matching data\splits\kip00/05/10/20.

## data\splits\
- primary\train.csv, kras_unseen\train.csv, cold\train.csv (validation and test files are in
  the code repository under data\splits\)
- ic50only\train.csv, valid.csv, test.csv
- kip00, kip05, kip10, kip20\train.csv, valid.csv, test.csv. Each train.csv is the
  129,043-row subsample used for training; valid and test are identical across the four.

## Not archived
- Cold-ligand OFF run: no prediction file (2-epoch reference run).
- IC50-only control runs: weights and predictions (split files and reported metrics only).
- Label-offset control runs: weights (split files and test-set predictions only).
