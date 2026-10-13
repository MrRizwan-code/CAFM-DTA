"""
make_cold_split.py -- rebuild the CAFM-DTA cold-ligand split from the primary split.

Recipe (verified to reproduce the published split row-for-row):
  1. Concatenate the primary train, valid and test files (in that order).
  2. Take unique ligands in order of first appearance.
  3. Shuffle them with numpy.random.default_rng(42).
  4. Assign the first 80% of ligands to train, the next 10% to valid, the rest to test.
     Every row follows its ligand, so no ligand appears in more than one split.

Expected output: train 229,289 / valid 28,849 / test 28,698 rows
                 (58,708 / 7,338 / 7,339 unique ligands; zero overlap).

Usage:
  python scripts/make_cold_split.py --primary_dir data/splits/primary --out_dir data/splits/cold
The primary train.csv is archived on Zenodo (too large for GitHub); download it into
data/splits/primary/ first. valid.csv and test.csv are already in the repository.
"""
import argparse, os
import numpy as np, pandas as pd

p = argparse.ArgumentParser()
p.add_argument("--primary_dir", default="data/splits/primary")
p.add_argument("--out_dir", default="data/splits/cold")
p.add_argument("--seed", type=int, default=42)
a = p.parse_args()

m = pd.concat([pd.read_csv(os.path.join(a.primary_dir, f"{s}.csv"))
               for s in ["train", "valid", "test"]], ignore_index=True)

ligs = m["Ligand"].unique()
np.random.default_rng(a.seed).shuffle(ligs)
n = len(ligs)
tr, va = set(ligs[:int(.8 * n)]), set(ligs[int(.8 * n):int(.9 * n)])
split = m["Ligand"].map(lambda l: "train" if l in tr else ("valid" if l in va else "test"))

os.makedirs(a.out_dir, exist_ok=True)
for s in ["train", "valid", "test"]:
    d = m[split == s].reset_index(drop=True)
    d.to_csv(os.path.join(a.out_dir, f"{s}.csv"), index=False)
    print(f"{s}: {len(d):,} rows, {d['Ligand'].nunique():,} ligands")
