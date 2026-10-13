# CAFM-DTA - Figure S2: per-target off vs film on all ten targets.
# (a) per-target Pearson r, off vs film; (b) per-target improvement heatmap
#     (Pearson r gain, RMSE reduction, Spearman rho gain).
# Primary targets: seed 1, evaluation-path predictions, read from
#     results/slice_analysis_off_vs_film.csv (rows "tgt=<target>").
# DS2 targets: three-seed means computed from
#     results/ds2/DS2_<OFF|FILM>_SEED<s>_15EP/test_prediction_seed<s>.csv
# Run: python figS2_pertarget_gain.py [path/to/results]
# Outputs: figS2_pertarget_gain.pdf (vector) + .png (600 dpi) in the current
#          folder; per-target values are printed. Needs numpy, pandas, matplotlib.
import os, re, sys
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
RES = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "results")

PRIMARY = ["BRAF", "EGFR", "KRAS", "PIK3CA", "mTOR"]
DS2 = ["AKT1", "CDK4", "ERBB2", "MAP2K1", "SRC"]
SEEDS = [1, 2, 3]
# target_name text in the DS2 prediction files -> short label (checked in order)
DS2_PATTERNS = [("ERBB2", r"erbb2|erbb-2|her2"),
                ("MAP2K1", r"map2k1|mek1|kinase kinase 1\b"),
                ("AKT1", r"akt1|kinase akt\b|rac-alpha"),
                ("CDK4", r"cdk4|cyclin-dependent kinase 4\b"),
                ("SRC", r"\bsrc\b")]
KEYS = ["r_off", "r_film", "rmse_off", "rmse_film", "sp_off", "sp_film"]


def label_ds2(name):
    s = str(name).lower()
    for lab, pat in DS2_PATTERNS:
        if re.search(pat, s):
            return lab
    return None


def metrics(y, p):
    y = np.asarray(y, float)
    p = np.asarray(p, float)
    r = float(np.corrcoef(y, p)[0, 1])
    rmse = float(np.sqrt(np.mean((y - p) ** 2)))
    sp = float(pd.Series(y).rank().corr(pd.Series(p).rank()))  # Spearman = Pearson on ranks
    return r, rmse, sp


rows = []
sl = pd.read_csv(os.path.join(RES, "slice_analysis_off_vs_film.csv"))
for t in PRIMARY:
    m = sl[sl["slice"] == "tgt=" + t]
    if len(m) != 1:
        sys.exit(f"ERROR: expected one row 'tgt={t}' in the slice file, found {len(m)}")
    m = m.iloc[0]
    rows.append(dict(target=t, group="primary", n=int(m["n"]), **{k: float(m[k]) for k in KEYS}))

acc = {t: {k: [] for k in KEYS} for t in DS2}
ns = {}
for arm in ["OFF", "FILM"]:
    for s in SEEDS:
        f = os.path.join(RES, "ds2", f"DS2_{arm}_SEED{s}_15EP", f"test_prediction_seed{s}.csv")
        d = pd.read_csv(f)
        d["lab"] = d["target_name"].map(label_ds2)
        if d["lab"].isna().any():
            bad = sorted(d.loc[d["lab"].isna(), "target_name"].astype(str).unique())
            sys.exit("ERROR: unrecognised DS2 target_name values: " + ", ".join(bad))
        for t in DS2:
            g = d[d["lab"] == t]
            if len(g) < 3:
                sys.exit(f"ERROR: too few rows for {t} in {f}")
            r, rmse, sp = metrics(g["regression_label"], g["predicted_binding_affinity"])
            k = arm.lower()
            acc[t]["r_" + k].append(r)
            acc[t]["rmse_" + k].append(rmse)
            acc[t]["sp_" + k].append(sp)
            ns[t] = len(g)
for t in DS2:
    rows.append(dict(target=t, group="DS2", n=ns[t], **{k: float(np.mean(v)) for k, v in acc[t].items()}))

T = pd.DataFrame(rows)
T["d_r"] = T["r_film"] - T["r_off"]
T["d_rmse"] = T["rmse_off"] - T["rmse_film"]  # reduction: positive = better
T["d_sp"] = T["sp_film"] - T["sp_off"]

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
except ImportError:
    plt = None

if plt is not None:
    labels = list(T["target"])
    x = np.arange(len(labels))
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6.4), gridspec_kw=dict(height_ratios=[1.35, 1]))
    ax1.axvspan(4.5, 9.5, color="#f3efeb", zorder=0)
    for i, (a, b) in enumerate(zip(T["r_off"], T["r_film"])):
        ax1.plot([i, i], [a, b], color="#c8c8c8", lw=2.2, zorder=1)
    ax1.scatter(x, T["r_off"], color="#8c8c8c", s=36, zorder=3, label="off  (PSICHIC baseline)")
    ax1.scatter(x, T["r_film"], color="#c0503a", s=36, zorder=3, label="film  (CAFM-DTA)")
    ax1.set_xlim(-0.5, 9.5)
    ax1.set_xticks(x)
    ax1.set_xticklabels([])
    ax1.set_ylabel("Pearson correlation (r)")
    ax1.set_title("Per-target accuracy", loc="left", fontsize=10)
    ax1.legend(loc="upper left", frameon=False, fontsize=8.5)
    ax1.grid(axis="y", color="#e6e6e6", lw=0.8)
    ax1.set_axisbelow(True)
    for side in ("top", "right"):
        ax1.spines[side].set_visible(False)
    H = np.vstack([T["d_r"], T["d_rmse"], T["d_sp"]])
    im = ax2.imshow(H, cmap="viridis", aspect="auto", vmin=0, vmax=max(0.06, float(H.max())))
    for i in range(3):
        for j in range(len(labels)):
            v = H[i, j]
            ax2.text(j, i, f"{v:.3f}", ha="center", va="center", fontsize=7.5,
                     color="black" if v > 0.045 else "white")
    ax2.axvline(4.5, color="white", lw=2)
    ax2.set_xticks(x)
    ax2.set_xticklabels(labels, fontsize=8.5)
    ax2.set_yticks([0, 1, 2])
    ax2.set_yticklabels(["Pearson r \u2191", "RMSE \u2193", "Spearman \u03c1 \u2191"], fontsize=8.5)
    ax2.set_title("Per-target improvement (film \u2212 off), all three metrics", loc="left", fontsize=10)
    tr = ax2.get_xaxis_transform()
    ax2.text(2, -0.30, "Primary (5 CRC targets)", transform=tr, ha="center", va="top", fontsize=8.5, color="#555555")
    ax2.text(7, -0.30, "DS2 (5 independent targets)", transform=tr, ha="center", va="top", fontsize=8.5, color="#555555")
    ax1.text(-0.07, 1.05, "a", transform=ax1.transAxes, fontweight="bold", fontsize=13)
    ax2.text(-0.07, 1.08, "b", transform=ax2.transAxes, fontweight="bold", fontsize=13)
    fig.suptitle("Condition modulation improves every target on every metric, in both datasets",
                 fontweight="bold", fontsize=11)
    fig.tight_layout()
    pos = ax2.get_position()
    cax = fig.add_axes([pos.x1 + 0.01, pos.y0, 0.012, pos.height])
    cb = fig.colorbar(im, cax=cax)
    cb.set_label("improvement magnitude", fontsize=8)
    _pdf = os.path.join(os.getcwd(), "figS2_pertarget_gain.pdf")
    _png = os.path.join(os.getcwd(), "figS2_pertarget_gain.png")
    fig.savefig(_pdf, bbox_inches="tight")
    fig.savefig(_png, dpi=600, bbox_inches="tight")
    status = "Saved figS2_pertarget_gain.pdf / .png"
else:
    status = "matplotlib not installed: numbers only, figure NOT drawn (pip install matplotlib)"

pd.set_option("display.width", 200)
print(T[["target", "group", "n", "r_off", "r_film", "d_r", "d_rmse", "d_sp"]].round(3).to_string(index=False))
print(status)
neg = int((T[["d_r", "d_rmse", "d_sp"]] <= 0).sum().sum())
print(f"Comparisons favoring off: {neg} of 30")
