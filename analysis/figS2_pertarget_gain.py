"""Compatibility entry point: regenerate corrected Figures 6 and S2."""
from pathlib import Path
import subprocess, sys
if __name__=='__main__':
    subprocess.run([sys.executable,str(Path(__file__).resolve().parents[1]/
                   'publication_figures/generate_corrected_figures.py')],check=True)
