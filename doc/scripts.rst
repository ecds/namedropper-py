Scripts
=======

:mod:`namedropper` command-line scripts

lookup-names
------------

**lookup-names** is a command-line script which uses a remote service
(currently DBpedia Spotlight) to identify and report on named resources, such
as Persons, Places, and Organizations which are identified in the content of a
plain text file, targeted sections of an Encoded Archival Description (EAD)
XML document, or user-specified sections of a Text Encoding Initiative (TEI)
XML document.  The script will attempt to auto-detect the input document type
(EAD, TEI, or plain text), but you can always explicitly set the document type
with the ``--input`` option.

Example usage::

  $ lookup-names /path/to/my/textfile.txt

  $ lookup-names findingaid.xml

To restrict the type of resources you want returned, or to adjust the minimum
confidence and support scores (e.g., to filter out erroneous matches), you can
pass specify additional parameters to be passed to the Spotlight service; for
example, to require a confidence score of at least 0.5, a support score of at
least 40, and restrict identified types to only Persons, Places, and
Organizations::

  $ lookup-names findingaid.xml --confidence 0.5 --support 40 --types "Person,Place,Organisation"

Because TEI document structure is so variable, when examining a TEI document
the script requires that you specify an XPath for the section of the document
which you want looked up.  When running in section-output (non-unique) mode,
the script will display the first ``docTitle`` or ``head`` under the specified
node as a section heading (currently only supports headings in the TEI
namespace).  The script currently considers XPath elements with the prefix
``t:`` to be in the TEI namespace.  Some examples of using the script for
different TEI documents::

  $ lookup-names essay.xml --tei-xpath t:text/t:body/t:div
  $ lookup-names newspaper_issue.xml --tei-xpath t:text/t:body/t:div1/t:div2
  $ lookup-names text_group_document.xml --tei-xpath //t:group/t:group/t:text

To see a unique, sorted list of names and corresponding resource URIs in any
input mode, use the ``--unique`` option.

To see the scores for items returned by DBpedia Spotlight (e.g., in order to
tune the confidence and support options for a given corpus), use the
``--scores`` option (cannot be used with ``--unique``).

.. Note::

  For large EAD documents, running this script is currently quite slow due to
  DBpedia Spotlight response times and the fact that individual paragraphs and
  container list descriptions are annotated individually.

CSV output
^^^^^^^^^^

Use the ``--csv`` option to generate a CSV file with more detailed information
about recognized names.  Along with the recognized text and the DBpedia URI, this
includes the support scores and some document context, to allow inspecting the results
for accuracy and determining a good support score setting for your content.

.. Note::

  When opening the CSV output file in Excel, you should open it as Unicode UTF-8.


Generate XML with tagged names
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To generate a new version of your EAD or TEI document with identified
resources tagged, use the ``--output`` (or ``-o``) option and specify the name
of the filename where you want the new version to be saved.  Note that this
feature is somewhat experimental.  Before using it, you should first run the
script and output the DBpedia annotation scores so that you can fine-tune the
results to exclude as many as bogus results as you can (e.g., by increasing
the minimum support score).  It is also recommended to restrict the types to
persons, places, and organizations (i.e., use ``--types Person,Place,Organisation``).
You should, of course, carefully review changes made to the output file before accepting
or using them.

.. Note::

  Due to the limitations of the software (DBpedia -> VIAF lookup is currently
  only implemented for personal names) and EAD name tags, which have
  attributes for authority control numbers (such as VIAF), but cannot
  reference a resource URI such as a DBpedia reference, non-personal names
  tagged in EAD will currently be added without any identifier or reference to
  the entity returned by DBpedia Spotlight.

count-nametags
--------------

**count-nametags** is a command-line script for reporting on the number of
tagged personal, corporate, and geographic names in a document.

For EAD documents, the script reports on the total number of ``persname``,
``corpname``, and ``geogname`` tags in the specified document and the number
of name tags with authority control, both the total by source and the
number of unique identifiers for each type of name.

.. Note::

  Currently only EAD documents are supported.

