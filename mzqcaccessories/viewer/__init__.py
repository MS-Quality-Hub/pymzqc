"""Static, browser-only mzQC viewer.

The viewer is plain HTML/CSS/JavaScript with no build step, so this folder can be
published as-is (e.g. on GitHub Pages). ``VIEWER_DIR`` lets Python code, such as
the online validator, serve the files.
"""
from pathlib import Path

VIEWER_DIR = Path(__file__).resolve().parent
