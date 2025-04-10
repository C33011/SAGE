# Configuration file for the Sphinx documentation builder.

import os
import sys
import datetime

# Add the source directory to the path so Sphinx can find the code
sys.path.insert(0, os.path.abspath('../src'))

# Project information
project = 'SAGE'
copyright = f'{datetime.datetime.now().year}, Tate Matthews'
author = 'Tate Matthews'

# The full version, including alpha/beta/rc tags
release = '0.1.0'

# General configuration
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',
    'sphinx.ext.intersphinx',
    'sphinx.ext.coverage',
    'sphinx.ext.todo',
    'sphinx_rtd_theme',
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# HTML output options
html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
html_title = f"SAGE {release} Documentation"
html_logo = "_static/logo.png"  # Add a logo if you have one
html_favicon = "_static/favicon.ico"  # Add a favicon if you have one

# Theme options
html_theme_options = {
    'navigation_depth': 4,
    'collapse_navigation': False,
    'sticky_navigation': True,
    'titles_only': False,
    'display_version': True,
}

# autodoc configuration
autodoc_member_order = 'bysource'
autodoc_typehints = 'description'
autodoc_class_signature = 'mixed'
add_module_names = False

# napoleon configuration for Google/NumPy style docstrings
napoleon_google_docstring = True
napoleon_numpy_docstring = False
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = True
napoleon_use_admonition_for_notes = True
napoleon_use_admonition_for_references = True
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_preprocess_types = True
