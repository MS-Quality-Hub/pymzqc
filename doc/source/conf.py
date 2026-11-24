# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys
from importlib.metadata import version as package_version
sys.path.insert(0, os.path.abspath('../../mzqc/'))

# -- Project information -----------------------------------------------------

project = 'pymzqc'
copyright = '2019-2027, Mathias Walzer'
author = 'Mathias Walzer'

# The full version, including alpha/beta/rc tags
release = f"v{package_version('pymzqc')}"


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = ['sphinx.ext.napoleon', 'sphinx.ext.graphviz',
    'sphinx.ext.inheritance_diagram', 'sphinx.ext.autosectionlabel',
    'myst_parser', 'nbsphinx',]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []

# The accessories pages include README.md files whose headings start below H1
# by design (they are nested into the reST section structure).
suppress_warnings = ['myst.header']

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'alabaster'
html_theme_options = {
    "description": "A python library to use mzQC files",
    'github_repo': 'pymzqc',
    'github_user': 'MS-Quality-hub',
    # The theme's GitHub button is a third-party iframe (ghbtns.com); a static
    # badge link in _templates/sidebarbadges.html replaces it.
    'github_button': False,
    # Below page_width alabaster switches to its single-column small-screen
    # layout. Above it, _static/custom.css lets the page grow with the window
    # (up to 1600px) instead of a fixed 1200px column.
    'page_width': '1000px',
    'sidebar_width': '280px',
    # Sphinx's basic theme caps the text column at 800px, which left an empty
    # band right of the text and wrapped long headings early.
    'body_max_width': 'none',
}
html_static_path = ['_static']
html_sidebars = {
        '**': [# located at _templates/
                'about.html',
                'navigation.html',
                'relations.html',
                'searchbox.html',
                'sidebarbadges.html',
            ]
        } # [![PyPi version](https://badgen.net/pypi/v/pymzqc/)](https://pypi.org/project/pymzqc/)


# -- mzQC Viewer -------------------------------------------------------------
# The browser viewer (mzqcaccessories/viewer) is static HTML/JS; publish it with
# the HTML docs under viewer/. (html_extra_path would copy the folder contents
# into the site root and replace the docs' index.html, hence this hook.)
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
VIEWER_SRC = os.path.join(REPO_ROOT, 'mzqcaccessories', 'viewer')
VIEWER_FILES = ['index.html', 'mzqc-viewer.css', 'mzqc-core.js', 'mzqc-plot.js', 'mzqc-viewer.js']
# Example files offered on the viewer docs page (published under viewer/examples/).
VIEWER_EXAMPLES = [
    os.path.join(VIEWER_SRC, 'tests', 'fixtures', 'showcase.mzQC'),
    os.path.join(REPO_ROOT, 'tests', 'examples', 'individual-runs.mzQC'),
]


def copy_viewer(app, exception):
    import shutil
    if exception is not None or app.builder.format != 'html':
        return
    target = os.path.join(app.outdir, 'viewer')
    os.makedirs(os.path.join(target, 'examples'), exist_ok=True)
    for name in VIEWER_FILES:
        shutil.copy2(os.path.join(VIEWER_SRC, name), target)
    for path in VIEWER_EXAMPLES:
        shutil.copy2(path, os.path.join(target, 'examples'))


def setup(app):
    app.connect('build-finished', copy_viewer)
