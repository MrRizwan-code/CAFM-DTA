# -*- coding: utf-8 -*-
"""
Fig 1 - CAFM-DTA architecture schematic (verified against code).

Backbone (grey, PSICHIC): drug & protein graphs -> PNA x3 -> attention-weighted
sum pooling (200 each) -> concat -> 400-d interaction fingerprint (blue).
Condition branch (terracotta): emb_std 32 + emb_assay 32 -> concat 64 ->
cond_mlp 64-64-64 (ReLU, dropout 0.1) -> to_gamma 400 / to_beta 400.
FiLM: gamma . feat + beta, gamma = 1 + to_gamma(c), zero-init (identity at start),
applied to the 400-d fingerprint -> regression head (MLP 400-200-1) -> affinity.

Verified: net.py lines 152-158, 326-344; condition_encoder.py; config.json
(hidden_channels=200 -> feat_dim = 200*2 = 400).

Standalone: pip install matplotlib ; run in VS Code for Arial-embedded copy.
"""
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from matplotlib import font_manager

mpl.rcParams["pdf.fonttype"] = 42
mpl.rcParams["ps.fonttype"] = 42
mpl.rcParams["svg.fonttype"] = "none"
for fam in ["Arial", "Helvetica", "Liberation Sans", "DejaVu Sans"]:
    if any(fam in f.name for f in font_manager.fontManager.ttflist):
        mpl.rcParams["font.family"] = fam
        break

# palette
G_FILL, G_EDGE, G_TXT = "#F1EFE8", "#5F5E5A", "#2C2C2A"
C_FILL, C_EDGE, C_TXT = "#FAECE7", "#993C1D", "#4A1B0C"
B_FILL, B_EDGE, B_TXT = "#E6F1FB", "#185FA5", "#042C53"
INK = "#2B2B2B"

fig, ax = plt.subplots(figsize=(7.2, 7.4))
ax.set_xlim(0, 680); ax.set_ylim(0, 700); ax.invert_yaxis(); ax.axis("off")

def box(x, y, w, h, fill, edge, lw=0.5):
    ax.add_patch(FancyBboxPatch((x, y), w, h,
        boxstyle="round,pad=0,rounding_size=8", mutation_aspect=1,
        facecolor=fill, edgecolor=edge, linewidth=lw, zorder=2))

def title(x, y, s, col, fs=10.5):
    ax.text(x, y, s, ha="center", va="center", fontsize=fs, fontweight="medium",
            color=col, zorder=3)

def sub(x, y, s, col, fs=9):
    ax.text(x, y, s, ha="center", va="center", fontsize=fs, color=col, zorder=3)

def hdr(x, y, s):
    ax.text(x, y, s, ha="center", va="center", fontsize=10.5, fontweight="medium",
            color=G_TXT, zorder=3)

def arrow(x1, y1, x2, y2):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2),
        arrowstyle="-|>", mutation_scale=10, linewidth=1.3,
        color=INK, shrinkA=0, shrinkB=0, zorder=1))

def elbow(pts):
    for i in range(len(pts) - 1):
        (x1, y1), (x2, y2) = pts[i], pts[i + 1]
        last = i == len(pts) - 2
        ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2),
            arrowstyle="-|>" if last else "-", mutation_scale=10 if last else 1,
            linewidth=1.3, color=INK, shrinkA=0, shrinkB=0, zorder=1))

# ---- backbone (grey) ----
hdr(160, 24, "PSICHIC backbone")
box(40, 44, 110, 50, G_FILL, G_EDGE);   title(95, 62, "Drug graph", G_TXT);   sub(95, 80, "SMILES", G_TXT)
box(210, 44, 110, 50, G_FILL, G_EDGE);  title(265, 62, "Protein graph", G_TXT); sub(265, 80, "sequence + ESM", G_TXT)
box(40, 118, 110, 52, G_FILL, G_EDGE);  title(95, 137, "Drug PNA x3", G_TXT);  sub(95, 156, "graph convs", G_TXT)
box(210, 118, 110, 52, G_FILL, G_EDGE); title(265, 137, "Protein PNA x3", G_TXT); sub(265, 156, "graph convs", G_TXT)
arrow(95, 94, 95, 118); arrow(265, 94, 265, 118)
box(40, 196, 110, 52, G_FILL, G_EDGE);  title(95, 215, "Attn-wtd", G_TXT);  sub(95, 234, "sum pool -> 200", G_TXT)
box(210, 196, 110, 52, G_FILL, G_EDGE); title(265, 215, "Attn-wtd", G_TXT); sub(265, 234, "sum pool -> 200", G_TXT)
arrow(95, 170, 95, 196); arrow(265, 170, 265, 196)
box(80, 272, 200, 52, B_FILL, B_EDGE)
title(180, 291, "Interaction fingerprint", B_TXT); sub(180, 310, "concat 200 + 200 -> 400", B_TXT)
elbow([(95, 248), (95, 298), (80, 298)])
elbow([(265, 248), (265, 298), (280, 298)])

# ---- condition branch (terracotta) ----
hdr(530, 24, "Condition branch")
box(410, 44, 100, 50, C_FILL, C_EDGE);  title(460, 62, "emb_std", C_TXT);  sub(460, 80, "32", C_TXT)
box(530, 44, 100, 50, C_FILL, C_EDGE);  title(580, 62, "emb_assay", C_TXT); sub(580, 80, "32", C_TXT)
box(410, 118, 220, 40, C_FILL, C_EDGE); title(520, 138, "concat -> 64", C_TXT)
arrow(460, 94, 460, 118); arrow(580, 94, 580, 118)
box(410, 182, 220, 54, C_FILL, C_EDGE)
title(520, 201, "cond_mlp  64-64-64", C_TXT); sub(520, 221, "ReLU, dropout 0.1", C_TXT)
arrow(520, 158, 520, 182)
box(410, 272, 100, 52, C_FILL, C_EDGE); title(460, 291, "to_gamma", C_TXT); sub(460, 310, "400", C_TXT)
box(530, 272, 100, 52, C_FILL, C_EDGE); title(580, 291, "to_beta", C_TXT);  sub(580, 310, "400", C_TXT)
elbow([(500, 236), (470, 272)]); elbow([(540, 236), (570, 272)])

# ---- FiLM + head ----
box(240, 392, 200, 76, C_FILL, C_EDGE, lw=1.2)
title(340, 414, "FiLM modulation", C_TXT)
sub(340, 434, "gamma . feat + beta", C_TXT)
sub(340, 452, "gamma = 1 + to_gamma, zero-init", C_TXT)
elbow([(180, 324), (180, 430), (240, 430)])
elbow([(460, 324), (460, 362), (360, 362), (360, 392)])
elbow([(580, 324), (580, 367), (400, 367), (400, 392)])
ax.text(210, 415, "feat 400", ha="center", va="center", fontsize=9, color=G_TXT)
ax.text(360, 350, "gamma", ha="center", va="center", fontsize=9, color=G_TXT)
ax.text(420, 378, "beta", ha="center", va="center", fontsize=9, color=G_TXT)
box(240, 512, 200, 52, G_FILL, G_EDGE)
title(340, 531, "Regression head", G_TXT); sub(340, 550, "MLP 400-200-1", G_TXT)
arrow(340, 468, 340, 512)
box(240, 612, 200, 44, G_FILL, G_EDGE); title(340, 634, "Predicted affinity", G_TXT)
arrow(340, 564, 340, 612)

fig.savefig("fig1_architecture.pdf", bbox_inches="tight")
fig.savefig("fig1_architecture.png", dpi=300, bbox_inches="tight")
print("saved")
