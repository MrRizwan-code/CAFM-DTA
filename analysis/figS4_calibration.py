#!/usr/bin/env python3
# =============================================================================
# Fig 7 - CAFM-DTA: Calibration / reliability (HONEST framing)
# =============================================================================
# Runs on CPU in VS Code:  pip install numpy matplotlib
#
# DATA IS EMBEDDED BELOW (contents of step12d_calibration.json, unchanged).
#   -> no external JSON needed. Just run this file.
#
# NOTE ON NUMBERING: per the locked lineup this becomes an SI figure (S1),
# with the cold-split leaderboard as main-text Fig 7. Filename left as-is for
# now to match your current re-render set; rename at the panel-arrangement step.
#
# HONEST FRAMING (locked): film is MORE accurate (lower MAE every seed) but has
# a small seed-dependent NEGATIVE bias that inflates ECE; the bias is a single
# correctable offset and does not change ranking.
#
# Outputs: figS4_calibration.pdf (vector) + .png (600 dpi), current folder
# =============================================================================

import os
import json

import numpy as np
import matplotlib as mpl
mpl.use("Agg")   # no GUI needed; guarantees the files get written
import matplotlib.pyplot as plt

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

# --- Embedded data (contents of step12d_calibration.json, unchanged) ----------
_DATA_JSON = r"""{
  "off": {
    "pred": [
      4.908280761134356,
      5.42176126493431,
      5.811243896535287,
      6.16184888464132,
      6.491393781427242,
      6.806290240855714,
      7.11250677367748,
      7.427874564573886,
      7.791439233821649,
      8.484248363749417
    ],
    "truth": [
      4.948575081357508,
      5.439808743169398,
      5.856968375770259,
      6.203237414254157,
      6.48664109716411,
      6.811648064178584,
      7.0918986164399485,
      7.397068364143704,
      7.766956749215208,
      8.4886209902371
    ],
    "ece_mean": 0.056447701839128735,
    "ece_sd": 0.008710939553036702
  },
  "film": {
    "pred": [
      4.795225457973036,
      5.278559716684106,
      5.661432839983722,
      6.021791487606092,
      6.357267954404928,
      6.683591183060109,
      7.014651123113592,
      7.363452704173933,
      7.772964679316359,
      8.539343763145048
    ],
    "truth": [
      4.923837749883774,
      5.405361585862109,
      5.800470875479594,
      6.169375653993721,
      6.5030398651789865,
      6.8023846064411115,
      7.09956865480758,
      7.416536449250088,
      7.81382455528427,
      8.557002556950255
    ],
    "ece_mean": 0.12653935952987136,
    "ece_sd": 0.05755112699211308
  },
  "per_seed_bias": {
    "off": [
      0.0484,
      -0.0064,
      -0.0643
    ],
    "film": [
      -0.158,
      0.0186,
      -0.1615
    ]
  },
  "per_seed_mae": {
    "off": [
      0.6366,
      0.6242,
      0.6161
    ],
    "film": [
      0.6159,
      0.5897,
      0.5974
    ]
  },
  "note": "film lower MAE every seed; calibration error driven by small seed-dependent negative bias, correctable by single validation offset; ranking unaffected"
}"""
d = json.loads(_DATA_JSON)

off_p = np.array(d["off"]["pred"]);  off_t = np.array(d["off"]["truth"])
fil_p = np.array(d["film"]["pred"]); fil_t = np.array(d["film"]["truth"])
bias = d["per_seed_bias"]

# -----------------------------------------------------------------------------
fig = plt.figure(figsize=(6.8, 3.1))
axA = fig.add_axes([0.085, 0.17, 0.36, 0.70])
axB = fig.add_axes([0.62, 0.17, 0.30, 0.70])

# ---- Panel a: reliability curve (quantity-only labels; quiet inline labels) --
lo, hi = 4.6, 8.8
axA.plot([lo, hi], [lo, hi], color=FAINT, lw=0.8, ls=(0, (4, 3)), zorder=1)
axA.plot(off_t, off_p, "-o", color=OFF, lw=1.0, ms=3.2, mew=0, zorder=2)
axA.plot(fil_t, fil_p, "-o", color=FILM, lw=1.0, ms=3.2, mew=0, zorder=3)

axA.set_xlim(lo, hi); axA.set_ylim(lo, hi); axA.set_aspect("equal")
axA.spines["top"].set_visible(False); axA.spines["right"].set_visible(False)
axA.spines["left"].set_bounds(5, 8); axA.spines["bottom"].set_bounds(5, 8)
axA.set_xticks([5, 6, 7, 8]); axA.set_yticks([5, 6, 7, 8])
axA.tick_params(length=2.5, pad=2)
axA.set_xlabel("Observed affinity", fontsize=7)
axA.set_ylabel("Predicted affinity", fontsize=7)
# quiet inline series labels (no legend box), placed off the crowded diagonal
axA.text(8.4, 8.05, "off", color=OFF, fontsize=6.3, ha="left", va="center",
         fontweight="bold")
axA.text(8.4, 7.55, "film (CAFM-DTA)", color=FILM, fontsize=6.3, ha="left",
         va="center", fontweight="bold")
axA.text(7.55, 7.78, "identity", color=FAINT, fontsize=6, rotation=45,
         rotation_mode="anchor", ha="center", va="center")

# ---- Panel b: per-seed bias (quantity-only label; house per-seed points) -----
axB.axhline(0.0, color=REF, lw=0.6, zorder=1)
for xc, (name, col, vals) in zip([0, 1],
        [("off", OFF, bias["off"]), ("film", FILM, bias["film"])]):
    vals = np.array(vals)
    m, sd = vals.mean(), vals.std(ddof=1)
    axB.plot([xc, xc], [m - sd, m + sd], color=col, lw=1.0, zorder=2)
    axB.plot([xc - 0.06, xc + 0.06], [m, m], color=col, lw=1.4, zorder=3)
    jit = (np.arange(len(vals)) - (len(vals) - 1) / 2) * 0.05
    axB.scatter(xc + jit, vals, s=20, facecolors="none", edgecolors=col,
                linewidths=0.8, zorder=4)

axB.set_xlim(-0.5, 1.5)
axB.set_xticks([0, 1])
axB.set_xticklabels(["off", "film\n(CAFM-DTA)"])
axB.set_ylim(-0.25, 0.25)
axB.set_yticks([-0.2, -0.1, 0.0, 0.1, 0.2])
axB.set_yticklabels([f"{t:g}".replace("-", MINUS) for t in axB.get_yticks()])
axB.spines["top"].set_visible(False); axB.spines["right"].set_visible(False)
axB.spines["bottom"].set_visible(False)
axB.spines["left"].set_bounds(-0.2, 0.2)
axB.tick_params(axis="x", length=0, pad=3)
axB.tick_params(axis="y", length=2.5, pad=2)
axB.set_ylabel(f"Prediction bias (pred {MINUS} truth)", fontsize=7)

# panel tags in figure space (consistent with Fig 5)
for ax, tag in [(axA, "a"), (axB, "b")]:
    pos = ax.get_position()
    fig.text(pos.x0 - 0.055, pos.y1 + 0.04, tag, fontsize=10, fontweight="bold",
             va="bottom", ha="left")

_pdf = os.path.join(os.getcwd(), "figS4_calibration.pdf")
_png = os.path.join(os.getcwd(), "figS4_calibration.png")
fig.savefig(_pdf)
fig.savefig(_png, dpi=600)
plt.close(fig)

print("Saved figS4_calibration.pdf / .png")
for _p in (_pdf, _png):
    ok = os.path.exists(_p); sz = os.path.getsize(_p) if ok else 0
    print(f"  [{'OK' if ok else 'MISSING'}] {_p}  ({sz:,} bytes)")
