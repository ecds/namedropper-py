Scripts
=======

:mod:`namedropper` command-line scripts

lookup-names
------------

**lookup-names** is a command-line script which uses a remote service (currently DBpedia Spotlight)
to identify and report on named resources, such as Persons, Places, and Organizations which are
identified in the content of a plain text file, targeted sections of an Encoded Archival
Description (EAD) XML document, or user-specified sections of a Text Encoding Initiative (TEI) XML
document.

Example usage::

  $ lookup-names --input text /path/to/my/textfile.txt

  $ lookup-names --input ead findingaid.xml

To restrict the type of resources you want returned, or to adjust the minimum confidence and support
scores (e.g., to filter out erroneous matches), you can pass specify additional parameters to be
passed to the Spotlight service; for example, to require a confidence score of at least 0.5, a support
score of at least 40, and restrict identified types to only Persons, Places, and Organizations::

  $ lookup-names --input ead findingaid.xml --confidence 0.5 --support 40 --types "Person,Place,Organisation"

Because TEI document structure is so variable, when examining a TEI document the script requires that you specify an XPath for the section of the document which you want looked up.  When running in section-output (non-unique) mode,
the script will display the first ``docTitle`` or ``head`` under the specified node as a section heading (currently only supports headings in the TEI namespace).  The script currently considers XPath elements with the prefix ``t:`` to be in the TEI namespace.  Some examples of using the script for different TEI documents::

  $ lookup-names --input tei essay.xml --tei-xpath t:text/t:body/t:div
  $ lookup-names --input tei newspaper_issue.xml --tei-xpath t:text/t:body/t:div1/t:div2
  $ lookup-names --input tei text_group_document.xml --tei-xpath //t:group/t:group/t:text

To see a unique, sorted list of names and corresponding resource URIs in any input mode, use the ``--unique`` option.

.. Note::

  For large EAD documents, running this script is currently quite slow due to DBpedia Spotlight response times
  and the fact that individual paragraphs and container list descriptions are annotated individually.