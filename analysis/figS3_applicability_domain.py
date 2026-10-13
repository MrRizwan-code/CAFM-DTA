#!/usr/bin/env python3
# =============================================================================
# Fig 8 - CAFM-DTA: Applicability domain (HONEST limitation figure)
# =============================================================================
# Runs on CPU in VS Code:  pip install numpy matplotlib
#
# DATA IS EMBEDDED BELOW (base64 of step12e_ad_curve.json, unchanged).
#   -> no external JSON needed. Just run this file.
#
# NOTE ON NUMBERING: per the locked lineup this becomes an SI figure (S2).
# Filename left as-is for now to match your current re-render set.
#
# HONEST FRAMING (locked): the test set is analogue-DENSE (93% of ligands have
# a nearest-train Tanimoto in 0.95-1.0). Performance degrades as chemistry
# becomes novel, for BOTH models. Novel-chemistry bins are tiny (<0.5 has n=72)
# so their numbers - including where film slightly trails - are underpowered.
#
# Outputs: figS3_applicability_domain.pdf (vector) + .png (600 dpi), current folder
# =============================================================================

import os
import base64
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

# --- Embedded data (base64 of step12e_ad_curve.json; decoded at runtime) ------
_DATA_B64 = """
ewogICJiaW5zIjogWwogICAgewogICAgICAiYmluIjogIjwwLjUiLAogICAgICAib2ZmX3IiOiAwLjM2NTMxMjg2Mzg1Njk4MDAz
LAogICAgICAiZmlsbV9yIjogMC4yOTY1MTc3MTE2OTY5Mjk3LAogICAgICAib2ZmX21hZSI6IDAuOTQ5OTc2NjMyODcwMzcwNCwK
ICAgICAgImZpbG1fbWFlIjogMC45NzI4MDgyMjIyMjIyMjIyLAogICAgICAibiI6IDcyCiAgICB9LAogICAgewogICAgICAiYmlu
IjogIjAuNS0wLjciLAogICAgICAib2ZmX3IiOiAwLjUxNzM3MzA2NzU0MjIwNjcsCiAgICAgICJmaWxtX3IiOiAwLjU1NTUxNDY3
NTY4MjAyOTMsCiAgICAgICJvZmZfbWFlIjogMC44NjcyNDc0OCwKICAgICAgImZpbG1fbWFlIjogMC44NTM5MjU2NjQzNzI3NTk5
LAogICAgICAibiI6IDQ2NQogICAgfSwKICAgIHsKICAgICAgImJpbiI6ICIwLjctMC44NSIsCiAgICAgICJvZmZfciI6IDAuNjM2
NTM1NTYwMDYyODY3NSwKICAgICAgImZpbG1fciI6IDAuNjU2NTcxNzM5MDgwNDY4NSwKICAgICAgIm9mZl9tYWUiOiAwLjc4MzA2
OTY4MzAzMDMwMzEsCiAgICAgICJmaWxtX21hZSI6IDAuNzY5NTE3Nzg2OTIxODUsCiAgICAgICJuIjogMTA0NQogICAgfSwKICAg
IHsKICAgICAgImJpbiI6ICIwLjg1LTAuOTUiLAogICAgICAib2ZmX3IiOiAwLjcxNTYxNTIxNTk1NDUwMzIsCiAgICAgICJmaWxt
X3IiOiAwLjcyOTAyODUxNDAzMDMxNDksCiAgICAgICJvZmZfbWFlIjogMC43NTAyMDU5NzA5NTExNTY3LAogICAgICAiZmlsbV9t
YWUiOiAwLjczMTg5MTgxMzQ1MzI5OTEsCiAgICAgICJuIjogMzg5CiAgICB9LAogICAgewogICAgICAiYmluIjogIjAuOTUtMS4w
IiwKICAgICAgIm9mZl9yIjogMC43OTk0ODg2NTU2NDQ4MTksCiAgICAgICJmaWxtX3IiOiAwLjgyNDM1OTE5NzM4NzA3MTksCiAg
ICAgICJvZmZfbWFlIjogMC42MTI1ODUxNTI2NTAyMzg1LAogICAgICAiZmlsbV9tYWUiOiAwLjU4NzA3ODE4MTM0MDk3MzIsCiAg
ICAgICJuIjogMjY3MDIKICAgIH0KICBdLAogICJtZWRpYW5fc2ltIjogMS4wCn0=
"""
d = json.loads(base64.b64decode(_DATA_B64).decode("utf-8"))
bins = d["bins"]
labels = [b["bin"] for b in bins]
off_r = np.array([b["off_r"] for b in bins])
fil_r = np.array([b["film_r"] for b in bins])
n = np.array([b["n"] for b in bins])
tot = n.sum()
pct = 100 * n / tot
xpos = np.arange(len(bins))

# -----------------------------------------------------------------------------
fig = plt.figure(figsize=(6.8, 3.2))
axA = fig.add_axes([0.085, 0.22, 0.37, 0.66])
axB = fig.add_axes([0.60, 0.22, 0.36, 0.66])

# ---- Panel a: Pearson r per similarity bin ----------------------------------
axA.plot(xpos, off_r, "-o", color=OFF, lw=1.0, ms=3.6, mew=0, zorder=2)
axA.plot(xpos, fil_r, "-o", color=FILM, lw=1.0, ms=3.6, mew=0, zorder=3)
axA.set_xlim(-0.4, len(bins) - 0.6)
axA.set_ylim(0.2, 0.9)
axA.set_xticks(xpos); axA.set_xticklabels(labels, rotation=30, ha="right")
axA.set_yticks([0.2, 0.4, 0.6, 0.8])
axA.spines["top"].set_visible(False); axA.spines["right"].set_visible(False)
axA.spines["left"].set_bounds(0.2, 0.8)
axA.spines["bottom"].set_bounds(0, len(bins) - 1)
axA.tick_params(length=2.5, pad=2)
axA.set_xlabel("Nearest-train Tanimoto similarity", fontsize=7)
axA.set_ylabel("Pearson r", fontsize=7)
# quiet inline series labels near the dense (right) end
axA.text(4.05, fil_r[-1] + 0.045, "film (CAFM-DTA)", color=FILM, fontsize=6.3,
         ha="right", va="bottom", fontweight="bold")
axA.text(4.05, off_r[-1] - 0.055, "off", color=OFF, fontsize=6.3,
         ha="right", va="top", fontweight="bold")

# ---- Panel b: test-point counts per bin, LINEAR, annotated ------------------
bars = axB.bar(xpos, n, width=0.62, color=FAINT, zorder=2)
bars[-1].set_color(FILM)   # highlight the dominant analogue-dense bin
axB.set_xlim(-0.6, len(bins) - 0.4)
axB.set_ylim(0, n.max() * 1.16)
axB.set_xticks(xpos); axB.set_xticklabels(labels, rotation=30, ha="right")
axB.set_yticks([0, 10000, 20000])
axB.set_yticklabels(["0", "10,000", "20,000"])
axB.spines["top"].set_visible(False); axB.spines["right"].set_visible(False)
axB.spines["left"].set_bounds(0, n.max())
axB.spines["bottom"].set_bounds(0, len(bins) - 1)
axB.tick_params(length=2.5, pad=2)
axB.set_xlabel("Nearest-train Tanimoto similarity", fontsize=7)
axB.set_ylabel("Test ligands (count)", fontsize=7)
# annotate each bar with n and percent
for xc, ni, pi in zip(xpos, n, pct):
    axB.text(xc, ni + n.max() * 0.02,
             "{:,}\n{:.1f}%".format(ni, pi), ha="center", va="bottom",
             fontsize=5.6, color=INK, linespacing=1.15)

# panel tags in figure space
for ax, tag in [(axA, "a"), (axB, "b")]:
    pos = ax.get_position()
    fig.text(pos.x0 - 0.055, pos.y1 + 0.045, tag, fontsize=10, fontweight="bold",
             va="bottom", ha="left")

_pdf = os.path.join(os.getcwd(), "figS3_applicability_domain.pdf")
_png = os.path.join(os.getcwd(), "figS3_applicability_domain.png")
fig.savefig(_pdf)
fig.savefig(_png, dpi=600)
plt.close(fig)

print("Saved figS3_applicability_domain.pdf / .png")
print("total test n:", tot, "| top-bin share: {:.1f}%".format(pct[-1]),
      "| median_sim:", d["median_sim"])
for _p in (_pdf, _png):
    ok = os.path.exists(_p); sz = os.path.getsize(_p) if ok else 0
    print("  [{}] {}  ({:,} bytes)".format("OK" if ok else "MISSING", _p, sz))
