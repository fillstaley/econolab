# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys
import importlib.metadata

# ─────── point Sphinx at your src/ layout ───────
sys.path.insert(0, os.path.abspath('../../src'))

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'EconoLab'
release = importlib.metadata.version("econolab")
author = 'Fill Staley'
copyright = '2025, Fill Staley'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',            # pull in docstrings
    'sphinx.ext.napoleon',           # NumPy & Google style
    'sphinx_autodoc_typehints',      # show PEP 484 annotations
    'sphinx.ext.viewcode',           # add “view source” links
]

templates_path = ['_templates']
exclude_patterns = ['_generated/*']



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
