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
sys.path.insert(0, os.path.abspath('../../mzqc/'))

# -- Project information -----------------------------------------------------

project = 'pymzqc'
copyright = '2019-2025, Mathias Walzer'
author = 'Mathias Walzer'

# The full version, including alpha/beta/rc tags
release = 'v1.0.0'


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

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'alabaster'
html_theme_options = {
    "description": "A python library to use mzQC files",
    'github_repo': 'pymzqc',
    'github_user': 'MS-Quality-hub',
    'page_width': '1200px',
    'sidebar_width': '280px;',
}
html_sidebars = {
        '**': [# located at _templates/
                'about.html',
                'navigation.html',
                'relations.html',
                'searchbox.html',
                'sidebarbadges.html',
            ]
        } # [![PyPi version](https://badgen.net/pypi/v/pymzqc/)](https://pypi.com/project/pymzqc)
