# Revision notes

This revision synchronizes existing verified corrections; it adds no new scientific experiment.

- Recovered simple_concat mode: main.py and models/condition_encoder.py.
- Corrected repeated-measurement export: utils/utils.py.
- Portable archived-checkpoint evaluator with explicit --release-root.
- Corrected Figure 6/S2 images, previews, per-target values, summaries and generators.
- Legacy Figure 6/S2 entry points now delegate; prepare_data validates rather than overwrites
  corrected inputs with old screening-path data.
- Documentation now describes actual GitHub contents, archive layout, pending IC50 evidence,
  and Figure 4 checkpoint attribution.

Unchanged: model backbone, training loop, primary/cold verified result values, external baseline
results and historical IC50 numbers. Historical files can contain superseded paths/claims;
read KNOWN_LIMITATIONS.md before using them.
