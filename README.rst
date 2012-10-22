name-dropper scripts
====================

Python scripts and utilities for looking up names and linking them to authoritative identifiers.

Use `pip <http://www.pip-installer.org/en/latest/index.html>`_ to install this package
and its dependencies::

    pip install .

If you want to run unit tests or generate documentation, install development dependencies::

    pip install -r pip-dev-req.txt

To run all unit tests::

    nosetests   # for normal development
    nosetests --with-coverage --cover-package=namedropper --cover-xml --with-xunit   # for continuous integration

To run unit tests for a specific module, use syntax like this::

    nosetests test/test_spotlight.py


To generate sphinx documentation::

    cd doc
    make html



