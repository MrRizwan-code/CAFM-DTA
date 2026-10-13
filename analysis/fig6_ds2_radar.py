#!/usr/bin/env python3
"""
CAFM-DTA — Figure 7: two-panel radar (cross-dataset transfer)
=============================================================
(a) Primary split (5 CRC targets): off vs film across the 4 metrics
(b) DS2 independent split (5 new targets): off vs film across the 4 metrics

Same off->film gap shape on both panels => the condition-modulation gain
replicates on an independent dataset.

RMSE is shown INVERTED (1 - RMSE) so that "outward = better" holds on every
axis. Both radars use the SAME tight radial range so the film edge sitting
outside off is visible and the two panels are directly comparable.

All values are ORIGINAL frozen best-validation-epoch numbers.
House palette: grey off / terracotta film. Arial, 600 dpi.
Outputs land NEXT TO THIS SCRIPT; paths are printed.
"""

import os
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

OUTDIR = os.path.dirname(os.path.abspath(__file__))

mpl.rcParams.update({
    "font.family": "Arial",
    "font.size": 11,
    "savefig.dpi": 600,
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
})

OFF_C  = "#8C8C8C"
FILM_C = "#D55E1A"
TXT    = "#222222"

# ------------------------------------------------------------ frozen data
# metric order around the radar
axes_labels = ["Pearson", "CI", "Spearman", "RMSE\n(inverted)"]

primary = {
    "off":  {"Pearson": 0.7893, "CI": 0.7976, "Spearman": 0.7871, "RMSE": 0.8160},
    "film": {"Pearson": 0.8137, "CI": 0.8106, "Spearman": 0.8122, "RMSE": 0.7822},
}
ds2 = {
    "off":  {"Pearson": 0.8216, "CI": 0.8179, "Spearman": 0.8193, "RMSE": 0.7935},
    "film": {"Pearson": 0.8392, "CI": 0.8314, "Spearman": 0.8402, "RMSE": 0.7648},
}

def to_axes(d):
    # Pearson, CI, Spearman as-is; RMSE inverted so outward = better
    return [d["Pearson"], d["CI"], d["Spearman"], 1 - d["RMSE"]]

# assemble all plotted radial values to fix a common tight range
all_vals = []
for D in (primary, ds2):
    for arm in ("off", "film"):
        all_vals += to_axes(D[arm])
lo = min(all_vals) - 0.01
hi = max(all_vals) + 0.01

N = len(axes_labels)
angles = np.linspace(0, 2*np.pi, N, endpoint=False).tolist()
angles += angles[:1]

def draw(ax, D, title):
    off_p  = to_axes(D["off"]);  off_p  += off_p[:1]
    film_p = to_axes(D["film"]); film_p += film_p[:1]
    ax.set_theta_offset(np.pi/2); ax.set_theta_direction(-1)
    ax.plot(angles, off_p,  color=OFF_C,  lw=2.0, label="off (PSICHIC)", zorder=2)
    ax.fill(angles, off_p,  color=OFF_C,  alpha=0.10, zorder=1)
    ax.plot(angles, film_p, color=FILM_C, lw=2.6, label="film (CAFM-DTA)", zorder=3)
    ax.fill(angles, film_p, color=FILM_C, alpha=0.16, zorder=2)
    ax.set_xticks(angles[:-1]); ax.set_xticklabels(axes_labels, fontsize=9.5)
    ax.set_ylim(lo, hi)
    ax.set_rlabel_position(90)
    ax.tick_params(axis='y', labelsize=7.5, colors="#777777")
    ax.set_title(title, fontsize=11, fontweight="bold", pad=18)

fig, (axA, axB) = plt.subplots(1, 2, figsize=(11.0, 5.6),
                               subplot_kw=dict(polar=True))
draw(axA, primary, "a   Primary (5 CRC targets)")
draw(axB, ds2,     "b   DS2 \u2014 independent (5 new targets)")

# shared legend below
handles, labels = axA.get_legend_handles_labels()
fig.legend(handles, labels, frameon=False, fontsize=9.5,
           loc="lower center", ncol=2, bbox_to_anchor=(0.5, 0.01))

fig.suptitle("Condition-modulation gain replicates on an independent dataset "
             "(outward = better on every axis)",
             fontsize=12, fontweight="bold", y=1.02)

fig.tight_layout(rect=[0, 0.05, 1, 1])
pdf_path = os.path.join(OUTDIR, "fig6_ds2_radar.pdf")
png_path = os.path.join(OUTDIR, "fig6_ds2_radar.png")
fig.savefig(pdf_path, bbox_inches="tight")
fig.savefig(png_path, bbox_inches="tight")
print("Saved:")
print("  " + pdf_path)
print("  " + png_path)
