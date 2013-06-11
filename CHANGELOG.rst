Change & Version Information
============================

The following is a summary of changes and improvements to
:mod:`namedropper`.  New features in each version should be listed, with
any necessary information about installation or upgrade notes.

0.3.1
-----

* Corrected CSV output of **lookup-names** script, which was broken in
  in 0.3.0.

0.3
---

* New script **count-nametags**

  * A user can run a script to get summary information about the number of
    tagged names in an EAD document, in order to do simple comparison of
    tagged and untagged documents.

* Updates to **lookup-names** script

  * When a user runs the lookup-names script to generate a CSV file, the resulting output
    includes resource type for person, place, or organization so that results can be
    filtered and organized by broad types.
  * When users interrupts the lookup-names script while it is running, it stops
    processing gracefully and reports on what was done so that user can get an idea
    of the output without waiting for the script to complete on a long document.
  * When a user runs the lookup names script with options that generate no results,
    the script does not create a CSV file or an enhanced xml file (even if those options
    were specified) and prints a message explaining why, so that the user is not confused
    by empty or unchanged files.
  * When users run the lookup-names script to generate annotated XML, they can optionally
    add tags with Oxygen history tracking comments so that changes can be reviewed and
    accepted or rejected in Oxygen.
  * Bug fix: When a user runs a lookup-names script on an XML file that does not have
    all of its component parts, it should not crash.
  * Bug fix: When annotating XML, the script will no longer crash if --types is not restricted
    to Person,Place,Organisation (or some subset of those three), and will warn about
    recognized entities that cannot be inserted into the output XML.
  * Bug fix: When annotating XML, tags will not be inserted where they are not schema valid
    (schema validation currently only supported for EAD).
  * Bug fix: If output XML is requested but an HTTP Proxy is not configured, the script will halt and
    information about setting a proxy, instead of crashing when attempting to validate the output XML.

0.2.1
-----

* Normalize whitespace for text context when generating CSV output
  (primarily affects plain-text input).

0.2
---

* A command-line user running the lookup-names script can have the input
  document type auto-detected, so they don't have to specify an input type
  every time they use the script.
* A command line user can run a script to look up recognized person names from
  a TEI or EAD XML document in a name authority system so that recognized
  names can be linked to other data.
* A command line user can run a script to generate a new version of an EAD XML
  document with tagged named entities, in order to automatically link
  mentioned entities to other data sources.
* A command line user can run a script to generate a new version of a TEI XML
  document with tagged named entities, in order to automatically link
  mentioned entities to other data sources.
* A command line user can optionally export identified resources and
  associated data to a CSV file, so they can review the results in more
  detail.

0.1
---

* New script **lookup-names**

  * A command line user can run a script to output recognized names in an EAD
    XML document in order to evaluate automated name recognition and
    disambiguation.
  * A command line user can run a script to output recognized names in a TEI XML
    document in order to evaluate automated name recognition and disambiguation.

