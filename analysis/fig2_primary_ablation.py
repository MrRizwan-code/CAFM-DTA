#!/usr/bin/env python3
# =============================================================================
# CAFM-DTA · Figure 2 — Primary-split ablation (off / concat / film)
# FINAL. Real per-seed points overlaid (matches PSICHIC convention),
# mean dots + SD error bars + progression trend line, hero (film) emphasized.
# JCIM: Arial, >=4.5 pt, >=0.5 pt lines, <=7 in wide, Okabe-Ito palette.
# Outputs: fig2_primary_ablation.pdf (vector) + .png (600 dpi)
#
# Reproducible on CPU:  pip install numpy matplotlib
#                       python fig2_primary_ablation.py
#
# All numbers FROZEN (from 12a/12b notebook outputs; best-validation-epoch test).
# off & film: 3 real per-seed values -> mean +/- SD.  concat: single seed.
# =============================================================================

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.lines import Line2D

for _f in ["Arial", "Helvetica", "Liberation Sans", "DejaVu Sans"]:
    if any(_f in f.name for f in font_manager.fontManager.ttflist):
        plt.rcParams["font.family"] = _f
        break

# ============================ FROZEN DATA (REAL) ============================
ORDER = ["off", "concat", "film"]

# real per-seed values (primary split, 3 seeds)
seed_vals = {
    "Pearson":  {"off": [0.7842, 0.7890, 0.7946], "film": [0.8068, 0.8165, 0.8179]},
    "RMSE":     {"off": [0.8242, 0.8157, 0.8080], "film": [0.7991, 0.7679, 0.7797]},
    "CI":       {"off": [0.7945, 0.7976, 0.8008], "film": [0.8065, 0.8123, 0.8130]},
    "Spearman": {"off": [0.7817, 0.7869, 0.7928], "film": [0.8048, 0.8150, 0.8167]},
}
# concat: single seed
concat_val = {"Pearson": 0.8028, "RMSE": 0.8014, "CI": 0.8047, "Spearman": 0.8017}

# means / SDs computed from the real seeds (population->sample SD, ddof=1 to match report)
mean = {m: {"off": np.mean(seed_vals[m]["off"]),
            "concat": concat_val[m],
            "film": np.mean(seed_vals[m]["film"])} for m in seed_vals}
sd = {m: {"off": np.std(seed_vals[m]["off"], ddof=1),
          "film": np.std(seed_vals[m]["film"], ddof=1)} for m in seed_vals}

higher_better = {"Pearson": True, "RMSE": False, "CI": True, "Spearman": True}
delta = {m: mean[m]["film"] - mean[m]["off"] for m in mean}
SIG = {"Pearson": "p = 0.0039"}   # paired t across seeds, n=3

COL = {"off": "#999999", "concat": "#0072B2", "film": "#D55E00"}

plt.rcParams.update({
    "font.size": 8,
    "axes.linewidth": 0.6, "axes.edgecolor": "#222222",
    "xtick.major.width": 0.6, "ytick.major.width": 0.6,
    "axes.grid": True, "grid.color": "#EEEEEE", "grid.linewidth": 0.5,
    "axes.axisbelow": True, "pdf.fonttype": 42, "ps.fonttype": 42,
})

metrics = ["Pearson", "RMSE", "CI", "Spearman"]
tags = ["(a)", "(b)", "(c)", "(d)"]
x = np.arange(len(ORDER))

fig, axes = plt.subplots(2, 2, figsize=(7.0, 5.8))
axes = axes.ravel()

for ax, m, tag in zip(axes, metrics, tags):
    yv = [mean[m][a] for a in ORDER]

    # progression trend line (under everything)
    ax.plot(x, yv, "-", color="#CCCCCC", lw=1.4, zorder=1)

    # REAL per-seed points (off, film), jittered slightly for visibility
    for xi, a in zip(x, ORDER):
        if a in seed_vals[m]:
            pts = seed_vals[m][a]
            jit = (np.arange(len(pts)) - (len(pts)-1)/2) * 0.055
            ax.scatter(xi + jit, pts, s=13, color=COL[a], alpha=0.45,
                       edgecolor="none", zorder=2)

    # mean dot + SD error bar (hero film larger)
    for xi, a in zip(x, ORDER):
        ye = sd[m].get(a)
        ms = 9.5 if a == "film" else 7.0
        ax.errorbar(xi, mean[m][a], yerr=ye, fmt="o", ms=ms, color=COL[a],
                    ecolor="#333333", elinewidth=1.0, capsize=3.5, capthick=1.0,
                    markeredgecolor="#222222",
                    markeredgewidth=(1.0 if a == "film" else 0.6), zorder=4)
        ax.annotate(f"{mean[m][a]:.4f}", (xi, mean[m][a]),
                    textcoords="offset points", xytext=(10, 0),
                    va="center", ha="left", fontsize=6.5,
                    fontweight=("bold" if a == "film" else "normal"),
                    color="#222222")

    allsd = [sd[m].get(a, 0) for a in ORDER]
    allpts = [p for a in seed_vals[m] for p in seed_vals[m][a]]
    lo = min(min(yv), min(allpts)) - 0.010
    hi = max(max(yv), max(allpts)) + 0.016
    ax.set_ylim(lo, hi)
    ax.set_xlim(-0.5, len(ORDER) - 0.5 + 0.45)

    arrow = "\u2191 higher is better" if higher_better[m] else "\u2193 lower is better"
    ax.set_title(f"{tag} {m}   ({arrow})", fontsize=8.5, fontweight="bold",
                 pad=6, loc="left")
    ax.set_xticks(x); ax.set_xticklabels(ORDER, fontsize=8)
    ax.tick_params(axis="y", labelsize=6.5)
    for s_ in ("top", "right"):
        ax.spines[s_].set_visible(False)

    dtxt = f"\u0394(film\u2212off) = {delta[m]:+.4f}"
    if m in SIG:
        dtxt += f",  {SIG[m]}"
    ax.text(0.5, -0.32, dtxt, transform=ax.transAxes, ha="center", va="top",
            fontsize=6.8, color="#333333")

axes[0].set_ylabel("Pearson r", fontsize=8)
axes[1].set_ylabel("RMSE (pChEMBL units)", fontsize=8)
axes[2].set_ylabel("Concordance index (CI)", fontsize=8)
axes[3].set_ylabel("Spearman \u03c1", fontsize=8)

handles = [
    Line2D([0],[0], marker="o", color="none", markerfacecolor=COL["off"],
           markeredgecolor="#222", markersize=7, label="off (PSICHIC baseline)"),
    Line2D([0],[0], marker="o", color="none", markerfacecolor=COL["concat"],
           markeredgecolor="#222", markersize=7, label="concat (single seed)"),
    Line2D([0],[0], marker="o", color="none", markerfacecolor=COL["film"],
           markeredgecolor="#222", markersize=8.5, label="film (CAFM-DTA)"),
    Line2D([0],[0], marker="o", color="none", markerfacecolor="#BBBBBB",
           markeredgecolor="none", alpha=0.5, markersize=6,
           label="individual seeds (n=3)"),
]
leg = fig.legend(handles=handles, loc="lower center", ncol=4, frameon=False,
                 fontsize=7, bbox_to_anchor=(0.5, -0.02))
for t in leg.get_texts():
    if "CAFM-DTA" in t.get_text():
        t.set_fontweight("bold")

fig.suptitle("Condition modulation (CAFM-DTA) improves all four metrics on the primary split",
             fontsize=9.5, fontweight="bold", y=0.997)

fig.tight_layout(rect=[0, 0.06, 1, 0.96])
fig.subplots_adjust(hspace=0.60, wspace=0.30)
fig.savefig("fig2_primary_ablation.pdf", bbox_inches="tight")
fig.savefig("fig2_primary_ablation.png", dpi=600, bbox_inches="tight")
print("saved fig2_primary_ablation.pdf (vector) + .png (600 dpi) — REAL per-seed points")
