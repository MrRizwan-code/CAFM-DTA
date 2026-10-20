# Publication figures

`figures/` contains 600 dpi PNG and vector PDF/SVG exports; `previews/` contains
smaller PNGs. Figures 6/S2 and their inputs were synchronized with the revised manuscript.
Other publication exports were preserved.

From the repository root:

```bash
python publication_figures/prepare_data.py
python publication_figures/generate_corrected_figures.py
```

The first command checks corrected DS2 per-target values against the six packaged
checkpoint reports without overwriting inputs. The second regenerates Figures 6/S2.
Use `--output-dir /another/folder` to preview without overwriting packaged exports.
`generate_figures.py` generates all figures and delegates Figures 6/S2 to this implementation.

Figure 4: archived CRC_COLD_FILM_converge, seed 1, assay B.
Figures 6/S2: corrected measurement-aligned DS2 checkpoint outputs, seeds 1–3;
primary statistics are unchanged. Source summaries are in results/.
Historical plotting sources/data are retained for provenance where not superseded;
they do not override the corrected generator.

`export_validation.json` records the dimensions, DPI and hashes of the current PNG exports.
Portable regeneration was tested locally for Figures 6/S2; full training was not performed.
