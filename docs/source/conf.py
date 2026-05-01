import os
import sys

# Ensure your project root is on path
sys.path.insert(0, os.path.abspath("../.."))

# -- Project information -----------------------------------------------------

project = "OWS Validation"
html_title = "OWS Validation Documentation"
html_short_title = "OWS Validation"
copyright = "2025, CT State - Office of Workforce Strategy"
author = "Michael Webb"
release = "1.1.2026"

# -- General configuration ---------------------------------------------------

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",   # Google / NumPy docstrings
    "sphinx.ext.viewcode",
]

templates_path = ["_templates"]
exclude_patterns = []

# Autodoc settings (important for your API docs)
autodoc_member_order = "bysource"
autodoc_typehints = "description"

# Napoleon settings (cleaner docstring parsing)
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = True

# -- HTML output -------------------------------------------------------------

# Recommended theme (install with: pip install furo)
html_theme = "furo"

html_theme_options = {
    "navigation_with_keys": True,
}

html_static_path = ["_static"]

# Optional custom CSS (create file if you want overrides)
html_css_files = [
    "custom.css",
]

# Code highlighting
pygments_style = "sphinx"

# -- Remove debug prints (no longer needed) ----------------------------------