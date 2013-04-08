#!/usr/bin/env python

# file namedropper-py/setup.py
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


from setuptools import setup, find_packages
import sys

from namedropper import __version__

LONG_DESCRIPTION = None
try:
    # read the description if it's there
    with open('README.rst') as desc_f:
        LONG_DESCRIPTION = desc_f.read()
except:
    pass

CLASSIFIERS = [
    'Development Status :: 2 - Pre-Alpha',
    'Environment :: Console',
    'Intended Audience :: Developers',
    'Intended Audience :: End Users/Desktop',
    #  'License :: OSI Approved :: Apache Software License',  License TBD
    'Natural Language :: English',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Topic :: Software Development :: Libraries :: Python Modules',
    'Topic :: Utilities',
]

# NOTE: a separate requirements file is needed for readthedocs.org
# If you add something here, you must also add it to pip-install-req.txt
install_requires = [
    'requests>=1.1.0',
    'eulxml',
    'rdflib',
    'feedparser',
    'unicodecsv==0.9.0',  # NOTE: temporary; 0.9.3 install is broken
    'python-dateutil',
]

extras_require = {
    # development dependencies for running unit tests and generating docs
    'dev': [
        'mock',
        'sphinx',
        'coverage',
        'nose'
    ]
}

#pip install package[extra]

if sys.version_info < (2, 7):
    install_requires.append("argparse==1.1")

setup(
    name='namedropper',
    version=__version__,
    author='Emory University Libraries',  # DiSC ?
    author_email='libsysdev-l@listserv.cc.emory.edu',
    url='https://github.com/emory-libraries-disc/name-dropper',
    license='Apache License, Version 2.0',
    packages=find_packages(),
    install_requires=install_requires,
    extras_require=extras_require,
    description='A collection of python utilities and scripts for identifying named entities in text and XML',
    long_description=LONG_DESCRIPTION,
    classifiers=CLASSIFIERS,
    scripts=[
        'scripts/lookup-names',
        'scripts/count-nametags',
    ],
)
