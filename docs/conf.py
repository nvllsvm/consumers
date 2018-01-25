import pkg_resources

project = 'consumers'
author = 'Andrew Rabert'
version = pkg_resources.get_distribution(project).version

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.intersphinx',
    'sphinx.ext.viewcode'
]

intersphinx_mapping = {'python': ('http://docs.python.org/3/', None)}

master_doc = 'index'
html_theme = 'sphinx_rtd_theme'
