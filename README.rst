name-dropper scripts
====================

Python scripts and utilities for looking up names and linking them to
authoritative identifiers.

Currently uses `DBpedia Spotlight`_ for recognition of named entities in text,
with support for matching identified DBpedia resources (currently only for
Persons) with the equivalent resource in `VIAF`_ (Virtual International
Authority File).

.. _DBpedia Spotlight: http://spotlight.dbpedia.org/
.. _VIAf: http://viaf.org


Installation
------------

We recommend the use of `pip <http://www.pip-installer.org/en/latest/index.html>`_
to install the latest released version of this package and its dependencies::

    $ pip install namedropper

This will also make the ``lookup-names`` script available.

Developer notes.
----------------

If you want to run unit tests or build sphinx documentation, you should also
install development dependencies::

    pip install -r pip-dev-req.txt

To run all unit tests::

    nosetests   # for normal development
    nosetests --with-coverage --cover-package=namedropper --cover-xml --with-xunit   # for continuous integration

To run unit tests for a specific module, use syntax like this::

    nosetests test/test_spotlight.py


To generate sphinx documentation::

    cd doc
    make html

