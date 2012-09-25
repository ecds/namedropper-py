# namedropper documentation build configuration file

import namedropper

extensions = ['sphinx.ext.autodoc', 'sphinx.ext.intersphinx']

#templates_path = ['templates']
exclude_trees = ['build']
source_suffix = '.rst'
master_doc = 'index'

project = 'namedropper'
copyright = '2012, Emory University Libraries'
version = '%d.%d' % namedropper.__version_info__[:2]
release = namedropper.__version__
modindex_common_prefix = ['namedropper.']

pygments_style = 'sphinx'

html_style = 'default.css'
#html_static_path = ['static']
htmlhelp_basename = 'namedropper'

latex_documents = [
  ('index', 'namedropper.tex', 'namedropper Documentation',
   'Emory University Libraries', 'manual'),
]

# configuration for intersphinx: refer to the Python standard library
intersphinx_mapping = {
    'python': ('http://docs.python.org/', None),
}
