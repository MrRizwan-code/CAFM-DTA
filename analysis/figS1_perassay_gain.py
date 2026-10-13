#!/usr/bin/env python3
# =============================================================================
# Fig 9 - CAFM-DTA: Per-assay accuracy gain (film over off)
# =============================================================================
# Runs on CPU in VS Code:  pip install numpy matplotlib
#
# DATA IS EMBEDDED BELOW (base64 of step12c_perassay.json, unchanged).
#   -> no external JSON needed. Just run this file.
#
# NOTE ON NUMBERING: per the locked lineup this becomes an SI figure (S3).
# Filename left as-is for now to match your current re-render set.
#
# WHAT THIS SHOWS
#   Pearson-r gain (film - off) for each measurement type. The gain is POSITIVE
#   for every assay and is LARGEST for the rarer, harder types (EC50, Kd) and
#   smallest for the common, well-covered ones (IC50, Ki) - mirroring the Fig 5
#   interpretability result that the condition branch helps most where data is
#   sparse and heterogeneous. The empty 'other' bin (NaN, n=0) is EXCLUDED.
#
# Outputs: figS1_perassay_gain.pdf (vector) + .png (600 dpi), current folder
# =============================================================================

import os
import math
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

# --- Embedded data (base64 of step12c_perassay.json; decoded at runtime) -------
_DATA_B64 = """
ewogICJJQzUwIjogewogICAgIm9mZiI6IDAuNzk5NzIxNDEwMzM0NTU1NSwKICAgICJmaWxtIjogMC44MTg4NTY2MTc1OTU5ODk3
LAogICAgImdhaW4iOiAwLjAxOTEzNTIwNzI2MTQzNDE0LAogICAgIm4iOiAxNzU5OAogIH0sCiAgIktpIjogewogICAgIm9mZiI6
IDAuNzY1MDE2MTIyMjc3NTYzLAogICAgImZpbG0iOiAwLjc4MjUyMjQ3NjczNjY2OTUsCiAgICAiZ2FpbiI6IDAuMDE3NTA2MzU0
NDU5MTA2NjQzLAogICAgIm4iOiA3NzYwCiAgfSwKICAiRUM1MCI6IHsKICAgICJvZmYiOiAwLjcwMjM2MzQyOTgyNzQxMTgsCiAg
ICAiZmlsbSI6IDAuNzgxNTM5MDUzOTAyMzg5MywKICAgICJnYWluIjogMC4wNzkxNzU2MjQwNzQ5Nzc2MiwKICAgICJuIjogMjE3
OQogIH0sCiAgIktkIjogewogICAgIm9mZiI6IDAuNzQ5NzI2Mjg3OTA4NTg1OCwKICAgICJmaWxtIjogMC43OTQ3MTg0MDY4NDk1
NzkzLAogICAgImdhaW4iOiAwLjA0NDk5MjExODk0MDk5MzQ5NiwKICAgICJuIjogOTkzCiAgfSwKICAib3RoZXIiOiB7CiAgICAi
b2ZmIjogTmFOLAogICAgImZpbG0iOiBOYU4sCiAgICAiZ2FpbiI6IE5hTiwKICAgICJuIjogMAogIH0KfQ==
"""
d = json.loads(base64.b64decode(_DATA_B64).decode("utf-8"))

# keep valid assays only (exclude NaN / n=0), order by n descending
recs = [(k, v) for k, v in d.items()
        if v["n"] > 0 and not (isinstance(v["gain"], float) and math.isnan(v["gain"]))]
recs.sort(key=lambda kv: kv[1]["n"], reverse=True)
assays = [k for k, _ in recs]
gain = np.array([v["gain"] for _, v in recs])
nvals = [v["n"] for _, v in recs]
xpos = np.arange(len(assays))

# x-tick labels with n integrated (house rule)
xticklabels = ["{}\nn = {:,}".format(a, n) for a, n in zip(assays, nvals)]

# -----------------------------------------------------------------------------
fig = plt.figure(figsize=(3.4, 3.2))
ax = fig.add_axes([0.19, 0.20, 0.74, 0.70])

ax.axhline(0.0, color=INK, lw=0.6, zorder=1)   # true zero baseline
bars = ax.bar(xpos, gain, width=0.60, color=FILM, zorder=2)

# value labels above each bar, consistent offset
ymax = gain.max()
for xc, g in zip(xpos, gain):
    ax.text(xc, g + ymax * 0.03, "+{:.3f}".format(g), ha="center", va="bottom",
            fontsize=6.2, color=INK)

ax.set_xlim(-0.6, len(assays) - 0.4)
ax.set_ylim(0, ymax * 1.18)
ax.set_xticks(xpos); ax.set_xticklabels(xticklabels)
ax.set_yticks([0, 0.02, 0.04, 0.06, 0.08])
ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
ax.spines["left"].set_bounds(0, 0.08)
ax.spines["bottom"].set_visible(False)
ax.tick_params(axis="x", length=0, pad=3)
ax.tick_params(axis="y", length=2.5, pad=2)
ax.set_ylabel(f"Pearson r gain, film (CAFM-DTA) {MINUS} off", fontsize=7)

# panel tag in figure space
pos = ax.get_position()
fig.text(pos.x0 - 0.135, pos.y1 + 0.03, "a", fontsize=10, fontweight="bold",
         va="bottom", ha="left")

_pdf = os.path.join(os.getcwd(), "figS1_perassay_gain.pdf")
_png = os.path.join(os.getcwd(), "figS1_perassay_gain.png")
fig.savefig(_pdf)
fig.savefig(_png, dpi=600)
plt.close(fig)

print("Saved figS1_perassay_gain.pdf / .png")
for a, g, n in zip(assays, gain, nvals):
    print("  {:5s} gain +{:.4f}  (n={:,})".format(a, g, n))
for _p in (_pdf, _png):
    ok = os.path.exists(_p); sz = os.path.getsize(_p) if ok else 0
    print("  [{}] {}  ({:,} bytes)".format("OK" if ok else "MISSING", _p, sz))
