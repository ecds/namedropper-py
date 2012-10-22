# file namedropper-py/doc/conf.py
#
#   Copyright 2012 Emory University Library
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

# namedropper documentation build configuration file

import os
import sys

on_rtd = os.environ.get('READTHEDOCS', None) == 'True'

if on_rtd:
    # read the docs build is failing because code is in a submodule
    # attempt to fix by adding module directory to python path
    docs_dir = os.path.dirname(os.path.abspath(__file__))
    module_dir = os.path.join(docs_dir, '..')
    sys.path.append(module_dir)

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
