import pkg_resources

project = 'consumers'
author = 'Andrew Rabert'
version = pkg_resources.get_distribution(project).version

extensions = ['sphinx.ext.autodoc']

html_theme_options = {}

html_theme = 'sphinx_rtd_theme'
