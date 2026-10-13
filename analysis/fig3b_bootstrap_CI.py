#!/usr/bin/env python3
"""
CAFM-DTA — Figure 3b rebuilt with bootstrap 95% CIs on the per-slice gain
=========================================================================
Adds uncertainty to the slice gains (All / Multi-assay / Single-assay) by
bootstrap-resampling the per-pair predictions, then redraws Fig 3 panel (b)
with 95% CI whiskers. Also prints CIs for the per-assay gains (S3).

>>> IMPORTANT: BOTH inputs must be the BIG per-pair prediction CSVs
    (~34 MB each), one OFF and one FILM:
        OFF_test_prediction_EVALPATH_*.csv    (unconditioned PSICHIC)
        FILM_test_prediction_EVALPATH_*.csv   (CAFM-DTA)
    Do NOT point either at slice_analysis_off_vs_film.csv (that is the
    14-row summary, not per-pair predictions).

Columns used: Protein, Ligand, standard_type, assay_type, reg_truth, reg_pred

The two files are aligned by MERGING on pair identity, so different row
ordering is fine. Slice rule (matches slice_analysis_off_vs_film.csv):
    MULTI  = (Protein,Ligand) pair occurs >1 time in the test set
    SINGLE = pair occurs exactly once
Gain: d_r = pearson_film - pearson_off per slice; 5,000 bootstrap resamples;
percentile 95% CI.

Run:  python fig3b_bootstrap_CI.py [OFF_predictions.csv FILM_predictions.csv]
Outputs land NEXT TO THIS SCRIPT: Fig3b_bootstrapCI.(pdf|png) + printed CIs.
"""

import os
import warnings
import numpy as np
warnings.filterwarnings('ignore', category=RuntimeWarning)
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt

# ============================ EDIT THESE TWO PATHS ============================
# Both must be the BIG *_test_prediction_EVALPATH_*.csv files (one OFF, one FILM)
import os, sys  # portable: pass OFF and FILM prediction CSVs as arguments, or place them next to this script
OFF_CSV  = sys.argv[1] if len(sys.argv) == 3 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "OFF_test_prediction_EVALPATH_seed1.csv")
FILM_CSV = sys.argv[2] if len(sys.argv) == 3 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "FILM_test_prediction_EVALPATH_seed1.csv")
# =============================================================================

OUTDIR = os.path.dirname(os.path.abspath(__file__))
N_BOOT = 5000
SEED   = 42

mpl.rcParams.update({
    "font.family": "Arial", "font.size": 11,
    "axes.spines.top": False, "axes.spines.right": False,
    "savefig.dpi": 600, "pdf.fonttype": 42, "ps.fonttype": 42,
})
OFF_C, FILM_C, CTX_C = "#8C8C8C", "#D55E1A", "#9FB6CC"

def pearson(a, b):
    if len(a) < 3: return np.nan
    return np.corrcoef(a, b)[0, 1]

KEYS = ["Protein", "Ligand", "standard_type", "assay_type", "reg_truth"]

# ----------------------------------------------------------------- load
off  = pd.read_csv(OFF_CSV)
film = pd.read_csv(FILM_CSV)

# guard against pointing at the summary file by mistake
for name, df in [("OFF", off), ("FILM", film)]:
    missing = [c for c in KEYS + ["reg_pred"] if c not in df.columns]
    if missing:
        raise SystemExit(
            f"\n[ERROR] {name} file is missing columns {missing}.\n"
            f"        Columns found: {list(df.columns)}\n"
            f"        Make sure {name}_CSV points at the BIG per-pair "
            f"*_test_prediction_EVALPATH_*.csv (not the slice summary)."
        )

print(f"Loaded OFF rows = {len(off):,} ; FILM rows = {len(film):,}")

# align by MERGING on pair identity (order-independent)
off_k  = off[KEYS + ["reg_pred"]].rename(columns={"reg_pred": "pred_off"})
film_k = film[KEYS + ["reg_pred"]].rename(columns={"reg_pred": "pred_film"})
merged = off_k.merge(film_k, on=KEYS, how="inner")
print(f"Matched pairs after merge = {len(merged):,}  (expected ~28,673)")
if len(merged) < 0.9 * min(len(off), len(film)):
    print("[WARN] Fewer matches than expected — check the two files are the "
          "OFF and FILM predictions from the SAME run/split.")

truth     = merged["reg_truth"].to_numpy()
pred_off  = merged["pred_off"].to_numpy()
pred_film = merged["pred_film"].to_numpy()

pair_key = (merged["Protein"].astype(str) + "||" + merged["Ligand"].astype(str))
counts   = pair_key.map(pair_key.value_counts())
is_multi = (counts > 1).to_numpy()
std_type = merged["standard_type"].astype(str).to_numpy()

masks = {
    "All pairs":    np.ones(len(truth), bool),
    "Multi-assay":  is_multi,
    "Single-assay": ~is_multi,
}

# ----------------------------------------------------------------- point estimates
point = {k: pearson(pred_film[m], truth[m]) - pearson(pred_off[m], truth[m])
         for k, m in masks.items()}

# ----------------------------------------------------------------- bootstrap
rng = np.random.default_rng(SEED)
N = len(truth)
boot = {k: np.empty(N_BOOT) for k in masks}
for b in range(N_BOOT):
    idx = rng.integers(0, N, N)
    t, po, pf = truth[idx], pred_off[idx], pred_film[idx]
    mm = is_multi[idx]; ss = ~mm
    boot["All pairs"][b]    = pearson(pf, t)          - pearson(po, t)
    boot["Multi-assay"][b]  = pearson(pf[mm], t[mm])  - pearson(po[mm], t[mm])
    boot["Single-assay"][b] = pearson(pf[ss], t[ss])  - pearson(po[ss], t[ss])

ci = {k: (np.nanpercentile(boot[k], 2.5), np.nanpercentile(boot[k], 97.5)) for k in masks}

print(f"\n=== Fig 3b slice gains with 95% bootstrap CI (n_boot={N_BOOT}) ===")
for k in masks:
    lo, hi = ci[k]
    print(f"  {k:13s}  d_r = {point[k]:+.4f}   95% CI [{lo:+.4f}, {hi:+.4f}]   n={int(masks[k].sum())}")

print("\n=== S1 per-assay gains with 95% bootstrap CI ===")
for a in ["IC50", "Ki", "EC50", "Kd"]:
    am = (std_type == a)
    if am.sum() < 3:
        print(f"  {a:5s}  (too few pairs: n={int(am.sum())})"); continue
    pe = pearson(pred_film[am], truth[am]) - pearson(pred_off[am], truth[am])
    aidx = np.where(am)[0]
    bb = np.empty(N_BOOT)
    for b in range(N_BOOT):
        s = rng.choice(aidx, len(aidx), replace=True)
        bb[b] = pearson(pred_film[s], truth[s]) - pearson(pred_off[s], truth[s])
    print(f"  {a:5s}  d_r = {pe:+.4f}   95% CI [{np.nanpercentile(bb,2.5):+.4f}, {np.nanpercentile(bb,97.5):+.4f}]   n={int(am.sum())}")

# ----------------------------------------------------------------- redraw Fig 3b
labels = ["All pairs", "Multi-assay", "Single-assay"]
x = np.arange(len(labels))
vals   = [point[k] for k in labels]
err_lo = [point[k]-ci[k][0] for k in labels]
err_hi = [ci[k][1]-point[k] for k in labels]
colors = [CTX_C, FILM_C, CTX_C]

fig, ax = plt.subplots(figsize=(5.2, 4.4))
ax.bar(x, vals, width=0.62, color=colors, edgecolor="black", linewidth=0.7,
       yerr=[err_lo, err_hi], capsize=5, error_kw=dict(elinewidth=1.3, ecolor="#333333"))
for xi, k in zip(x, labels):
    ax.text(xi, ci[k][1] + 0.002, f"+{point[k]:.4f}", ha="center", va="bottom",
            fontsize=9.5, fontweight="bold" if k == "Multi-assay" else "normal")
ax.axhline(0, color="#333333", lw=0.9)
ax.set_ylabel("\u0394 Pearson r  (film \u2212 off)", fontsize=10.5)
ax.set_xticks(x)
ax.set_xticklabels([f"{k}\nn = {int(masks[k].sum()):,}" for k in labels], fontsize=9.5)
ax.set_ylim(0, max(ci[k][1] for k in labels) * 1.2)
ax.set_title("Per-slice gain with 95% bootstrap CI", fontsize=11, fontweight="bold", loc="left")
ax.yaxis.grid(True, color="#ECECEC", lw=0.8); ax.set_axisbelow(True)

fig.tight_layout()
pdf = os.path.join(OUTDIR, "Fig3b_bootstrapCI.pdf")
png = os.path.join(OUTDIR, "Fig3b_bootstrapCI.png")
fig.savefig(pdf, bbox_inches="tight"); fig.savefig(png, bbox_inches="tight")
print("\nSaved:\n  " + pdf + "\n  " + png)
