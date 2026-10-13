#!/usr/bin/env python3
# =============================================================================
# Fig 5 - CAFM-DTA: FiLM condition-branch interpretability (gamma / beta)
# =============================================================================
# Runs on CPU in VS Code:  pip install numpy matplotlib
#
# DATA IS EMBEDDED BELOW (contents of filmparam_analysis.json, unchanged).
#   -> no external JSON needed. Just run this file.
#
# WHAT THIS SHOWS  (two panels)
#   a) Mean FiLM scale gamma per standard_type (assay), assay_type=B fixed.
#      gamma is negative; it becomes MORE negative (|gamma| larger) for rarer,
#      noisier assays -> stronger multiplicative modulation where measurements
#      are least standardised. IC50 (most common) = mildest; 'other' = strongest.
#      beta ~ 0 across all assays (reported in caption) -> modulation is
#      effectively multiplicative, not additive.
#   b) 5x5 cosine-similarity matrix of the per-assay gamma vectors. Off-diagonal
#      values 0.75-0.95 -> structured separation: the branch learns a distinct
#      but related transform per assay (not identical, not orthogonal).
#
# ASSAY_ORDER is the verified row/column order for BOTH gamma_mean and the
# cosine matrix {IC50:0,Ki:1,EC50:2,Kd:3,other:4}.
#
# Outputs: fig4_gamma_beta_interpretability.pdf (vector) + .png (600 dpi), current folder
# =============================================================================

import os
import json

import numpy as np
import matplotlib as mpl
mpl.use("Agg")   # no GUI needed; guarantees the files get written
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

# -----------------------------------------------------------------------------
# Locked house palette (shared across all figures)
# -----------------------------------------------------------------------------
OFF, FILM, REF = "#B0B0B0", "#C65A28", "#8FA9C0"
INK, FAINT = "#2B2B2B", "#8A8A8A"
MINUS = "\u2212"

mpl.rcParams.update({
    "pdf.fonttype": 42, "ps.fonttype": 42,
    "font.family": "sans-serif",
    "font.sans-serif": ["Arial", "Helvetica", "Liberation Sans", "DejaVu Sans"],
    "axes.linewidth": 0.5, "axes.edgecolor": INK,
    "xtick.major.width": 0.5, "ytick.major.width": 0.5,
    "xtick.color": INK, "ytick.color": INK,
    "text.color": INK, "axes.labelcolor": INK,
    "font.size": 7, "axes.grid": False,
})

# Verified assay order (rows/cols of both outputs).
ASSAY_ORDER = ["IC50", "Ki", "EC50", "Kd", "other"]

# --- Embedded data (contents of filmparam_analysis.json, unchanged) ----------
_DATA_JSON = r"""{"gamma_mean": {"IC50": -0.5169034004211426, "Ki": -0.6501175165176392, "EC50": -0.7812426090240479, "Kd": -0.7589381337165833, "other": -1.0416980981826782}, "gamma_cosine_matrix": [[1.0, 0.9043776988983154, 0.8805034160614014, 0.8536356687545776, 0.9044066071510315], [0.9043776988983154, 0.9999999403953552, 0.8008758425712585, 0.8437027335166931, 0.858439028263092], [0.8805034160614014, 0.8008758425712585, 1.0000004768371582, 0.807026743888855, 0.7525201439857483], [0.8536356687545776, 0.8437027335166931, 0.807026743888855, 0.9999999403953552, 0.9532783627510071], [0.9044066071510315, 0.858439028263092, 0.7525201439857483, 0.9532783627510071, 1.0000001192092896]], "note": "assay=B fixed; gamma primarily multiplicative, beta~0"}"""
d = json.loads(_DATA_JSON)

gamma = np.array([d["gamma_mean"][a] for a in ASSAY_ORDER], dtype=float)
C = np.array(d["gamma_cosine_matrix"], dtype=float)
assert C.shape == (5, 5), "cosine matrix is not 5x5"

# -----------------------------------------------------------------------------
# Figure: two panels side by side
# -----------------------------------------------------------------------------
fig = plt.figure(figsize=(6.8, 3.0))          # double column ~173 mm
axA = fig.add_axes([0.085, 0.20, 0.34, 0.66])  # panel a: gamma dot plot
axB = fig.add_axes([0.605, 0.20, 0.30, 0.66])  # panel b: heatmap (square-ish)

# ---- Panel a: gamma per assay, ordered so |gamma| increases downward --------
order_a = np.argsort(gamma)[::-1]              # least negative (top) -> most (bottom)
g_sorted = gamma[order_a]
labels_a = [ASSAY_ORDER[i] for i in order_a]
ypos = np.arange(len(g_sorted))[::-1]         # top row = first

axA.axvline(0.0, color=REF, lw=0.6, zorder=1)  # gamma = 0 reference
# stems from zero to the point (clean, honest, no bar inflation)
for y, g in zip(ypos, g_sorted):
    axA.plot([0, g], [y, y], color=FAINT, lw=0.8, zorder=2)
axA.scatter(g_sorted, ypos, s=26, c=FILM, zorder=3, linewidths=0)

axA.set_yticks(ypos)
axA.set_yticklabels(labels_a)
axA.set_ylim(-0.6, len(g_sorted) - 0.4)
axA.set_xlim(-1.15, 0.05)
axA.set_xticks([-1.0, -0.75, -0.5, -0.25, 0.0])
axA.set_xticklabels([f"{t:g}".replace("-", MINUS) for t in axA.get_xticks()])
axA.spines["top"].set_visible(False); axA.spines["right"].set_visible(False)
axA.spines["left"].set_visible(False)
axA.spines["bottom"].set_bounds(-1.0, 0.0)
axA.tick_params(axis="y", length=0, pad=3)
axA.tick_params(axis="x", length=2.5, pad=2)
# direction indicator INSIDE the axis title
axA.set_xlabel(f"Mean FiLM scale $\\gamma$  (more negative $\\rightarrow$ stronger modulation)",
               fontsize=7)

# ---- Panel b: 5x5 cosine heatmap -------------------------------------------
cmap = LinearSegmentedColormap.from_list("house_terra", ["#FBF3EE", "#C65A28"])
off = C[~np.eye(5, dtype=bool)]
vmin, vmax = 0.0, 1.0
im = axB.imshow(C, cmap=cmap, vmin=vmin, vmax=vmax, aspect="equal")

axB.set_xticks(range(5)); axB.set_yticks(range(5))
axB.set_xticklabels(ASSAY_ORDER, rotation=45, ha="right")
axB.set_yticklabels(ASSAY_ORDER)
axB.tick_params(length=0, pad=2)
for s in axB.spines.values():
    s.set_visible(False)

# annotate each cell; text colour flips for contrast on dark cells
for i in range(5):
    for j in range(5):
        val = C[i, j]
        tcol = "white" if val >= 0.78 else INK
        axB.text(j, i, f"{val:.2f}", ha="center", va="center",
                 fontsize=6, color=tcol)

# slim colourbar
cbar = fig.colorbar(im, ax=axB, fraction=0.046, pad=0.04, ticks=[0,0.25,0.5,0.75,1.0])
cbar.outline.set_linewidth(0.5)
cbar.ax.tick_params(length=2.5, width=0.5, labelsize=6)
cbar.set_label("cosine similarity", fontsize=6.5)

# -----------------------------------------------------------------------------
# Panel tags in figure space (consistent with Fig 2-4)
# -----------------------------------------------------------------------------
for ax, tag in [(axA, "a"), (axB, "b")]:
    pos = ax.get_position()
    fig.text(pos.x0 - 0.055, pos.y1 + 0.045, tag, fontsize=10,
             fontweight="bold", va="bottom", ha="left")

# -----------------------------------------------------------------------------
# Save vector PDF + 600 dpi PNG in the current folder
# -----------------------------------------------------------------------------
_pdf = os.path.join(os.getcwd(), "fig4_gamma_beta_interpretability.pdf")
_png = os.path.join(os.getcwd(), "fig4_gamma_beta_interpretability.png")
fig.savefig(_pdf)
fig.savefig(_png, dpi=600)
plt.close(fig)

print("Saved fig4_gamma_beta_interpretability.pdf / .png")
print("gamma:", dict(zip(ASSAY_ORDER, gamma.round(4))))
print("cosine off-diagonal range: %.3f - %.3f" % (off.min(), off.max()))
for _p in (_pdf, _png):
    ok = os.path.exists(_p); sz = os.path.getsize(_p) if ok else 0
    print(f"  [{'OK' if ok else 'MISSING'}] {_p}  ({sz:,} bytes)")
