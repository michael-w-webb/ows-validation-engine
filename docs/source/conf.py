import os
import sys

sys.path.insert(0, os.path.abspath("../.."))

# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'OWS Validation'
html_title = "OWS Validation"
html_short_title = "OWS Validation"
copyright = '2025, CT State - Office of Workforce Strategy'
author = 'Michael Webb'
release = '1.1.2026'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [    
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",   # for Google / NumPy style docstrings
    "sphinx.ext.viewcode",
    ]

templates_path = ['_templates']
exclude_patterns = []



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'alabaster'

html_theme_options = {
    "sidebar_header": "OWS Validation"
}

html_static_path = ['_static']

import sys
print("=== Sphinx sys.path ===")
for p in sys.path[:5]:
    print(p)
print("======================")