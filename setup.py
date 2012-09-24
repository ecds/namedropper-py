#!/usr/bin/env python

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

install_requires = [
    'requests',
    'eulxml',
]
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
    description='A collection of python utilities and scripts for identifying named entities in text and XML',
    long_description=LONG_DESCRIPTION,
    classifiers=CLASSIFIERS,
    scripts=[
        'scripts/lookup-names',
    ],
)
