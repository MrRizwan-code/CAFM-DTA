#!/usr/bin/env python3
# =============================================================================
# CAFM-DTA · Figure 3 — Where the gain concentrates: multi- vs single-assay pairs
# HOUSE STYLE: Nature/Cell minimal. Labels disciplined: direction lives in the
# axis title; panel tags (a/b) spaced above; no floating annotations.
# DATA IS EMBEDDED BELOW (copied verbatim from slice_analysis_off_vs_film.csv) --
#   -> no external CSV needed. Just run this file.
# Run: pip install numpy pandas matplotlib ; python fig3a_multi_vs_single.py
# Outputs: fig3a_multi_vs_single.pdf (vector) + .png (600 dpi) in the current folder
# =============================================================================

import os
import io
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")   # no GUI needed; guarantees the files get written
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.lines import Line2D

# --- Data embedded directly (only the 3 slices Fig 3 uses; values unchanged) --
_CSV = """slice,n,r_off,r_film,d_r
FULL,28673,0.7842219680646207,0.8068410868892764,0.022619118824655615
MULTI-assay,5029,0.7148542492610649,0.7872975421593553,0.07244329289829043
SINGLE-assay,23644,0.7966118639196146,0.8082998094602116,0.011687945540597044
"""
df = pd.read_csv(io.StringIO(_CSV)).set_index("slice")

# --- Font: embed Arial if present, else fall back silently -------------------
for _f in ["Arial", "Helvetica", "Liberation Sans", "DejaVu Sans"]:
    if any(_f in f.name for f in font_manager.fontManager.ttflist):
        plt.rcParams["font.family"] = _f
        print(f"[fig3] font: {_f}")
        break

SLICES = ["FULL", "MULTI-assay", "SINGLE-assay"]
disp = {"FULL": "All pairs", "MULTI-assay": "Multi-assay", "SINGLE-assay": "Single-assay"}
r_off  = [df.loc[s, "r_off"]  for s in SLICES]
r_film = [df.loc[s, "r_film"] for s in SLICES]
d_r    = [df.loc[s, "d_r"]    for s in SLICES]
n_obs  = [int(df.loc[s, "n"]) for s in SLICES]
ratio  = d_r[1] / d_r[2]

# muted palette
C_OFF, C_FILM, C_REF = "#B0B0B0", "#C65A28", "#8FA9C0"
INK, FAINT = "#2B2B2B", "#8A8A8A"
MINUS = "\u2212"

plt.rcParams.update({
    "font.size": 8,
    "axes.linewidth": 0.5, "axes.edgecolor": "#4D4D4D",
    "xtick.major.width": 0.5, "ytick.major.width": 0.5,
    "xtick.major.size": 2.5, "ytick.major.size": 2.5,
    "xtick.color": "#4D4D4D", "ytick.color": "#4D4D4D",
    "axes.grid": False, "pdf.fonttype": 42, "ps.fonttype": 42,
})

# extra top margin so panel tags + subtitles never touch the axes
fig, (axL, axR) = plt.subplots(1, 2, figsize=(7.0, 3.7),
                               gridspec_kw={"width_ratios": [1.1, 1.0]})
x = np.arange(len(SLICES))

# ============================ PANEL a: dumbbell ============================
for xi, ro, rf in zip(x, r_off, r_film):
    axL.plot([xi, xi], [ro, rf], "-", color="#DADADA", lw=2.2, zorder=1,
             solid_capstyle="round")
axL.scatter(x, r_off,  s=42, color=C_OFF,  edgecolor="white", linewidth=0.8, zorder=3)
axL.scatter(x, r_film, s=52, color=C_FILM, edgecolor="white", linewidth=0.8, zorder=3)
for xi, ro, rf in zip(x, r_off, r_film):
    axL.annotate(f"{rf:.3f}", (xi, rf), textcoords="offset points",
                 xytext=(9, 1), fontsize=6.6, fontweight="bold", color=INK)
    axL.annotate(f"{ro:.3f}", (xi, ro), textcoords="offset points",
                 xytext=(9, -1), va="top", fontsize=6.6, color=FAINT)

axL.set_ylim(0.70, 0.83)
axL.set_xlim(-0.45, 2.45)
axL.set_xticks(x)
axL.set_xticklabels([f"{disp[s]}\nn = {n:,}" for s, n in zip(SLICES, n_obs)],
                    fontsize=7.3, color=INK)
# DIRECTION lives in the axis title (not floating in the plot)
axL.set_ylabel("Pearson r  (\u2191 higher is better)", fontsize=8.5, color=INK)
for s_ in ("top", "right"): axL.spines[s_].set_visible(False)
axL.spines["left"].set_bounds(0.70, 0.82)
axL.legend(handles=[
    Line2D([0],[0], marker="o", color="none", markerfacecolor=C_OFF,
           markeredgecolor="white", markersize=6.5, label="off (PSICHIC)"),
    Line2D([0],[0], marker="o", color="none", markerfacecolor=C_FILM,
           markeredgecolor="white", markersize=7, label="film (CAFM-DTA)"),
], fontsize=6.8, frameon=False, loc="lower left", handletextpad=0.3,
   bbox_to_anchor=(0.02, 0.02))

# ============================ PANEL b: gain bars ==========================
cols = [C_REF, C_FILM, C_REF]
axR.bar(x, d_r, width=0.58, color=cols, edgecolor="none", zorder=3)
for xi, dv in zip(x, d_r):
    is_multi = SLICES[int(xi)] == "MULTI-assay"
    axR.annotate(f"+{dv:.4f}", (xi, dv), textcoords="offset points",
                 xytext=(0, 4), ha="center", fontsize=6.8,
                 fontweight=("bold" if is_multi else "normal"), color=INK)
axR.set_ylim(0, max(d_r) * 1.24)
axR.set_xlim(-0.6, 2.55)
axR.set_xticks(x)
axR.set_xticklabels([disp[s] for s in SLICES], fontsize=7.3, color=INK)
axR.set_ylabel(f"\u0394 Pearson r  (film {MINUS} off)", fontsize=8.5, color=INK)
for s_ in ("top", "right"): axR.spines[s_].set_visible(False)
axR.spines["left"].set_bounds(0, max(d_r))
axR.annotate(f"{ratio:.1f}\u00d7 larger than\nsingle-assay pairs",
             xy=(1, d_r[1] * 0.5), xytext=(2.02, d_r[1] * 0.66),
             fontsize=7.0, fontweight="bold", color=INK, ha="center",
             arrowprops=dict(arrowstyle="-|>", color="#666", lw=0.8,
                             connectionstyle="arc3,rad=-0.25"))

# ============ panel tags + subtitles: placed in FIGURE space, above axes ===
# compute each axes' top-left in figure coords so tags never overlap plot
fig.canvas.draw()
for ax, tag, sub in [(axL, "a", "Accuracy by pair type"),
                     (axR, "b", "Where the gain concentrates")]:
    bb = ax.get_position()
    fig.text(bb.x0, bb.y1 + 0.055, tag, fontsize=11, fontweight="bold",
             color=INK, ha="left", va="bottom")
    fig.text(bb.x0 + 0.028, bb.y1 + 0.058, sub, fontsize=8.2, color=FAINT,
             ha="left", va="bottom")

fig.suptitle("Condition-modulation gain concentrates on multi-assay pairs",
             fontsize=9.5, fontweight="bold", y=1.06, color=INK)
fig.subplots_adjust(wspace=0.34, bottom=0.20, top=0.82, left=0.09, right=0.97)

_pdf = os.path.join(os.getcwd(), "fig3a_multi_vs_single.pdf")
_png = os.path.join(os.getcwd(), "fig3a_multi_vs_single.png")
fig.savefig(_pdf, bbox_inches="tight")
fig.savefig(_png, dpi=600, bbox_inches="tight")
plt.close(fig)

print(f"saved fig3 (clean labels) ; ratio = {ratio:.2f}x")
for _p in (_pdf, _png):
    ok = os.path.exists(_p)
    sz = os.path.getsize(_p) if ok else 0
    print(f"  [{'OK' if ok else 'MISSING'}] {_p}  ({sz:,} bytes)")
