Scripts
=======

:mod:`namedropper` command-line scripts

lookup-names
------------

**lookup-names** is a command-line script which uses a remote service (currently DBpedia Spotlight)
to identify and report on named resources, such as Persons, Places, and Organizations which are
identified in the content of a plain text file or in targeted sections of an Encoded Archival
Description (EAD) XML document.

Example usage::

  $ lookup-names --input text /path/to/my/textfile.txt

  $ lookup-names --input ead findingaid.xml

To restrict the type of resources you want returned, or to adjust the minimum confidence and support
scores (e.g., to filter out erroneous matches), you can pass specify additional parameters to be
passed to the Spotlight service; for example, to require a confidence score of at least 0.5, a support
score of at least 40, and restrict identified types to only Persons, Places, and Organizations::

  $ lookup-names --input ead findingaid.xml --confidence 0.5 --support 40 --types "Person,Place,Organisation"

To see a unique, sorted list of names and corresponding resource URIs, use the ``--unique`` option.

.. Note::

  For large EAD documents, running this script is currently quite slow due to DBpedia Spotlight response times
  and the fact that individual paragraphs and container list descriptions are annotated individually.