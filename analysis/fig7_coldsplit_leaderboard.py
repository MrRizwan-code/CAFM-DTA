# -*- coding: utf-8 -*-
"""
Fig 10 - Cold-ligand split leaderboard (baseline comparison)  [3-panel]
CAFM-DTA (Condition-Aware Feature Modulation for Drug-Target Affinity)

Cold-ligand split: zero train/test ligand overlap; test n = 28,698.
Each model at its best training budget; best-validation-epoch -> test metrics.
XGBoost excluded (locked decision).

Panels:
  a  Pearson r   (higher better)  - all four models
  b  RMSE        (lower better)   - all four models
  c  Robustness: Pearson drop from the standard (overlap-heavy) split to the
     cold-ligand (novel-molecule) split, for the two PSICHIC arms. The
     unconditioned backbone (off) collapses on the honest split; film
     (CAFM-DTA) degrades far less -> conditioning buys robustness to novel
     chemistry. (Ablation-relevant contrast; baselines not on standard split.)

'off' in panels a/b is the unconditioned PSICHIC backbone shown as a REFERENCE
anchor (5-epoch), styled apart and labelled as such - not a best-budget peer.

Frozen values:
  Cold-ligand (Table 2 / ColdSplit handoff):
    off 0.6346 / 1.0311 (ref, 5 ep) ; DeepDTA 0.7004 / 0.9783 ;
    GraphDTA 0.7425 / 0.8998 ; film 0.7570 / 0.8785 (15 ep, ep14 best-val)
  Standard split (Table 2, PSICHIC arms only):
    off 0.7893 ; film 0.8137

Standalone: pip install numpy matplotlib ; run in VS Code for Arial-embedded copy.
"""

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager

# ---- Locked house style -----------------------------------------------------
mpl.rcParams["pdf.fonttype"] = 42
mpl.rcParams["ps.fonttype"] = 42
mpl.rcParams["svg.fonttype"] = "none"
for fam in ["Arial", "Helvetica", "Liberation Sans", "DejaVu Sans"]:
    if any(fam in f.name for f in font_manager.fontManager.ttflist):
        mpl.rcParams["font.family"] = fam
        break
mpl.rcParams["font.size"] = 7
mpl.rcParams["axes.linewidth"] = 0.5

C_OFF  = "#B0B0B0"
C_FILM = "#C65A28"
C_BASE = "#8FA9C0"
INK    = "#2B2B2B"
FAINT  = "#8A8A8A"

MODEL = "film\n(CAFM-DTA)"

# ---- Data (frozen) ----------------------------------------------------------
labels  = ["off\n(PSICHIC)\nref \u00b7 5 ep", "DeepDTA", "GraphDTA", MODEL]
pearson = [0.6346, 0.7004, 0.7425, 0.7570]
rmse    = [1.0311, 0.9783, 0.8998, 0.8785]
colors  = [C_OFF, C_BASE, C_BASE, C_FILM]
is_hero = [False, False, False, True]
is_ref  = [True,  False, False, False]

std_off,  cold_off  = 0.7893, 0.6346
std_film, cold_film = 0.8137, 0.7570

# ---- Layout -----------------------------------------------------------------
fig = plt.figure(figsize=(7.4, 3.0))
gs = fig.add_gridspec(1, 3, width_ratios=[1.0, 1.0, 0.85],
                      left=0.072, right=0.985, top=0.80, bottom=0.20, wspace=0.46)
axA = fig.add_subplot(gs[0]); axB = fig.add_subplot(gs[1]); axC = fig.add_subplot(gs[2])
x = np.arange(len(labels))

ymin_a, ymax_a = 0.60, 0.78
ymin_b, ymax_b = 0.85, 1.05

def style_bar_axis(ax, ymin, ymax):
    ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
    ax.spines["left"].set_bounds(ymin, ymax)
    ax.spines["left"].set_color(INK); ax.spines["bottom"].set_color(INK)
    ax.tick_params(width=0.5, length=3, colors=INK)
    ax.set_xticks(x); ax.set_xticklabels(labels, fontsize=6.0)
    ax.set_xlim(-0.6, len(labels) - 0.4)

def draw_bars(ax, vals, ymin, span):
    for xi, (val, col, hero, ref) in enumerate(zip(vals, colors, is_hero, is_ref)):
        ax.bar(xi, val - ymin, bottom=ymin, width=0.62, color=col,
               edgecolor=INK, linewidth=0.5, zorder=3,
               hatch="///" if ref else None)
        ax.text(xi, val + span * 0.02, "%.4f" % val, ha="center", va="bottom",
                fontsize=6.3, color=INK, fontweight="bold" if hero else "normal")

# Panel a
draw_bars(axA, pearson, ymin_a, ymax_a - ymin_a)
axA.set_ylim(ymin_a, ymax_a + 0.012); axA.set_yticks(np.arange(0.60, 0.79, 0.04))
axA.set_ylabel("Pearson r  (\u2191 higher is better)", fontsize=7, color=INK)
style_bar_axis(axA, ymin_a, ymax_a)

# Panel b
draw_bars(axB, rmse, ymin_b, ymax_b - ymin_b)
axB.set_ylim(ymin_b, ymax_b + 0.012); axB.set_yticks(np.arange(0.85, 1.06, 0.05))
axB.set_ylabel("RMSE  (\u2193 lower is better)", fontsize=7, color=INK)
style_bar_axis(axB, ymin_b, ymax_b)

# Panel c - shrinkage slopes
xc = [0, 1]
axC.plot(xc, [std_off, cold_off],   "-o", color=C_OFF,  markersize=5,
         markeredgecolor=INK, markeredgewidth=0.5, linewidth=1.2, zorder=3)
axC.plot(xc, [std_film, cold_film], "-o", color=C_FILM, markersize=5,
         markeredgecolor=INK, markeredgewidth=0.5, linewidth=1.4, zorder=4)
axC.text(1.05, cold_off,  "off\n\u2212%.3f" % (std_off - cold_off),
         va="center", ha="left", fontsize=6.0, color="#7d7d7d", fontweight="bold")
axC.text(1.05, cold_film, "film (CAFM-DTA)\n\u2212%.3f" % (std_film - cold_film),
         va="center", ha="left", fontsize=6.0, color=C_FILM, fontweight="bold")
axC.text(-0.05, std_off,  "%.4f" % std_off,  va="bottom", ha="right", fontsize=6.0, color=INK)
axC.text(-0.05, std_film, "%.4f" % std_film, va="bottom", ha="right", fontsize=6.0, color=INK)
axC.text(-0.05, cold_off,  "%.4f" % cold_off,  va="top", ha="right", fontsize=6.0, color=INK)
axC.text(-0.05, cold_film, "%.4f" % cold_film, va="top", ha="right", fontsize=6.0, color=INK)
axC.set_xlim(-0.42, 2.05); axC.set_ylim(0.60, 0.84)
axC.set_yticks(np.arange(0.60, 0.85, 0.05))
axC.set_xticks([0, 1]); axC.set_xticklabels(["Standard\n(overlap)", "Cold\n(novel)"], fontsize=6.3)
axC.spines["top"].set_visible(False); axC.spines["right"].set_visible(False)
axC.spines["left"].set_bounds(0.60, 0.84)
axC.spines["left"].set_color(INK); axC.spines["bottom"].set_color(INK)
axC.tick_params(width=0.5, length=3, colors=INK)
axC.set_ylabel("Pearson r", fontsize=7, color=INK)

# ---- Panel tags -------------------------------------------------------------
def panel_tag(ax, tag, subtitle):
    pos = ax.get_position()
    fig.text(pos.x0 - 0.050, pos.y1 + 0.055, tag, fontsize=9,
             fontweight="bold", va="bottom", ha="left", color=INK)
    fig.text(pos.x0 + 0.006, pos.y1 + 0.060, subtitle, fontsize=6.3,
             va="bottom", ha="left", color=FAINT)

panel_tag(axA, "a", "Correlation")
panel_tag(axB, "b", "Error")
panel_tag(axC, "c", "Robustness: standard \u2192 cold")

fig.savefig("fig7_coldsplit_leaderboard.pdf")
fig.savefig("fig7_coldsplit_leaderboard.png", dpi=600)
print("saved")
