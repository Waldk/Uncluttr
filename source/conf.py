# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'Uncluttr'
copyright = '2025, Cérina ALLEK, Waldeck FELIX, Rafael GONÇALVES, Alban HOELLINGER, Baptiste LE SCIELLOUR, Eva SUPIOT'
author = 'Cérina ALLEK, Waldeck FELIX, Rafael GONÇALVES, Alban HOELLINGER, Baptiste LE SCIELLOUR, Eva SUPIOT'
release = '0.0.4'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = []

templates_path = ['_templates']
exclude_patterns = []



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'alabaster'
html_static_path = ['_static']
extensions = ['sphinx.ext.autodoc']

