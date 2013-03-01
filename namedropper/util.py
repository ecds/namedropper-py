# file namedropper-py/namedropper/util.py
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

from datetime import datetime
from dateutil.tz import tzlocal
import logging
from lxml.etree import XMLSyntaxError, parse, ProcessingInstruction
from rdflib import Graph, Namespace, URIRef
import re
from namedropper import spotlight, viaf

logger = logging.getLogger(__name__)


def autodetect_file_type(filename):
    '''Attempt to auto-detect input file type.  Currently supported types are EAD XML, TEI XML,
    or text.  Any document that cannot be loaded as XML is assumed to be text.

    :returns: "tei", "ead", "text", or None if file type is not recognized
    '''
    # attempt to auto-detect input file type
    try:
        # load as generic xml
        generic_xml = parse(filename)
        root_element = generic_xml.getroot().tag
        # do a simple check on the root element (ignoring namespaces)
        if root_element.endswith('TEI'):
            return 'tei'
        elif root_element.endswith('ead'):
            return 'ead'

    except XMLSyntaxError:
        # Failure to parse as any kind of XML should mean text input.
        # If we need to be more fine-grained, could check error text;
        # should be something similar to this:
        #   Start tag expected, '<' not found, line 1, column 1
        return 'text'
        logger.info('Could not parse %s as XML, assuming text input' % \
            filename)


_viafids = {}
'dictionary mapping dbpedia URIs to VIAF ids, to avoid repeat lookups'
_dbpedia_viaf_lookups = []
'list of dbpedia URIs that have been looked up in VIAF, to avoid repeat lookups'

OWL = Namespace('http://www.w3.org/2002/07/owl#')
':class:`rdflib.Namespace` for OWL (Web Ontology Language)'


# FIXME: rename for clarity? really getting viaf uri;
# perhaps move this logic into dbpedia resource object?
def get_viafid(resource):
    '''Search VIAF for a DBpedia resource to find the equivalent resource.
    Currently only supports Persons; uses the owl:sameAs relation in VIAF data
    to confirm that the correct resource has been found.

    :params resource: dict for a single dbpedia resource, as included in
        :meth:`namedropper.spotlight.SpotlightClient.annotate` results
    :returns: matching VIAF URI, or None if no match was found
    '''
    res = spotlight.DBpediaResource(resource['URI'])
    if res.uri not in _viafids:
        viafid = None
        viafclient = viaf.ViafClient()

        # if we haven't already done so, check for viaf id in dbpedia first
        if res.uri not in _dbpedia_viaf_lookups:
            _dbpedia_viaf_lookups.append(res.uri)
            viafid = res.viafid
            if viafid:
                # store url format, for consistency with viaf search results
                _viafids[res.uri] = 'http://viaf.org/viaf/%s' % viafid

        # if viaf id was not found in dbpedia, look in viaf
        if not viafid:
            # TODO: fall-back label? what should this actually do here?
            if res.label is None:
                return None

            results = []
            # search for corresponding viaf resource by type
            if res.is_person:
                results = viafclient.find_person(res.label)

            # NOTE: only persons in VIAF have the dbpedia sameAs rel
            # For now, only implementing person-name VIAF lookup

            g = Graph()

            # iterate through results and look for a result that has
            # an owl:sameAs relation to the dbpedia resource
            for result in results:
                viaf_uriref = URIRef(result['link'])
                # load the RDF for the VIAF entity and parse as an rdflib graph
                g.parse(result['link'])
                # check for the triple we're interested in
                if (viaf_uriref, OWL['sameAs'], res.uriref) in g:
                    viafid = result['link']
                    _viafids[res.uri] = viafid
                    break

    return _viafids.get(res.uri, None)


NORMALIZE_WHITESPACE_RE = re.compile('\s\s+', flags=re.MULTILINE)


def normalize_whitespace(txt, next=None, prev=None):
    '''Normalize whitespace in a string to match the logic
    of ``normalize-space()`` in XPath.  Replaces all internal sequences
    of white space with a single space and conditionally removes
    leading and trailing whitespace.

    :param txt: text string to be normalized
    :param next: optional next string; used to determine
        if trailing whitespace should be removed
    :param prev: optional preceding string; used to determine
        if leading whitepace should be removed
    '''
    txt = NORMALIZE_WHITESPACE_RE.sub(' ', txt)
    if not next or next.startswith(' '):
        txt = txt.rstrip()
    if not prev or prev.endswith(' '):
        txt = txt.lstrip()

    return txt


def is_person(item):
    item_types = [i.strip() for i in item['types'].split(',')]
    return 'DBpedia:Person' in item_types or 'Freebase:/people/person' in item_types


def is_org(item):
    item_types = [i.strip() for i in item['types'].split(',')]
    return 'DBpedia:Organisation' in item_types


def is_place(item):
    item_types = [i.strip() for i in item['types'].split(',')]
    return 'DBpedia:Place' in item_types


def enable_oxygen_track_changes(node):
    oxy_track_changes = ProcessingInstruction('oxy_options',
        'track_changes="on"')
    node.append(oxy_track_changes)


def annotate_xml(node, result, mode='tei', track_changes=False):
    '''Annotate xml based on dbpedia spotlight annotation results.  Assumes
    that dbpedia annotate was called on the **normalized** text from this node.
    Currently updates the node that is passed in; whitespace will be normalized in text
    nodes where name tags are inserted.  For TEI, DBpedia URIs are inserted as
    **ref** attributes; since EAD does not support referencing URIs, VIAF ids
    will be used where possible (currently only supports lookup for personal names).

    If recognized names are already tagged as names in the existing XML, no
    new name tag will be inserted; attributes will only be added if they are not
    present in the original node.

    Currently using :mod:`logging` (info and warn) when VIAF look-up fails or
    attributes are not inserted to avoid overwriting existing values.

    When track changes is requested, processing instructions will be added
    around annotated names for review in OxygenXML 14.2+.  In cases where
    a name was untagged, the text will be marked as a deletion and the
    tagged version of the name will be marked as an insertion with a comment
    containing the description of the DBpedia resource, to aid in identifying
    whether the correct resource has been added.  If a recognized name was
    previously tagged, a comment will be added indicating what attributes
    were added, or would have been added if they did not conflict with
    attributes already present in the document.  When using the
    track changes option, it is recommended to also run meth:`enable_oxygen_track_changes`
    once on the document, so that Oxygen will automatically open
    the document with track changes turned on.

    :param node: lxml element node to be updated
    :param result: dbpedia spotlight result, as returned by
        :meth:`namedropper.spotlight.SpotlightClient.annotate`
    :param track_changes: mark changes using OxygenXML track changes
         processing instructions, to enable review in OxygenXML author mode

    :returns: total count of the number of entities inserted into the xml
    '''
    # TEI tags will all use name
    if mode == 'tei':
        name_tag = 'name'
        # create the new node in the same namespace as its parent
        if node.nsmap and node.prefix in node.nsmap:
            name_tag = '{%s}%s' % (node.nsmap[node.prefix], name_tag)

    # find all text nodes under this node
    text_list = node.xpath('.//text()')

    # get the list of identified resources from the dbpedia spotlight result
    resources = list(result['Resources'])

    # starting values
    current_offset = 0  # current index into the node
    inserted = 0  # number of items inserted into the xml
    item = None  # current dbpedia item being processed

    # aggregate of all normalized text before the current node
    # (used for whitespace normalization on the current node)
    # NOTE: aggregating all previous text in order to properly handle cases where there
    # are multiple whitespace-only nodes in a row
    prev_text = ''

    if track_changes:
        # generate timestamp to be used for Oxygen track changes
        # format Oxygen requires to be recognized: 20130227T165821-0500
        now = datetime.now(tzlocal())
        timestamp = now.strftime('%Y%m%dT%H%M%S%z')

    # iterate until we run out of text nodes or resources
    while (item or resources) and text_list:
        # if there is no current item, get the next item
        if item is None:
            item = resources.pop(0)
            item_offset = int(item['offset'])
            item_end_offset = item_offset + len(item['surfaceForm'])

            # determine the tag name to be used for this item
            # TODO/NOTE: might be worth refactoring tag name/attribute logic into
            # a separate function
            tei_type = None
            if is_person(item):
                tei_type = 'person'
                ead_tag = 'persname'
            elif is_org(item):
                tei_type = 'org'
                ead_tag = 'corpname'
            elif is_place(item):
                tei_type = 'place'
                ead_tag = 'geogname'
            else:
                # use generic fallback tag for ead if we can't identify the resource type
                ead_tag = 'name'

            if mode == 'ead':
                name_tag = ead_tag
                # create the new node in the same namespace as its parent
                if node.nsmap and node.prefix in node.nsmap:
                    name_tag = '{%s}%s' % (node.nsmap[node.prefix], name_tag)

        # current text node to be updated
        text_node = text_list.pop(0)
        next_text = text_list[0] if text_list else ''
        normalized_text = normalize_whitespace(unicode(text_node), next_text, prev_text)
        text_end_offset = current_offset + len(normalized_text)
        # get the parent node for the current text
        parent_node = text_node.getparent()
        # find node immediately after the current text node, so we know where to insert name tags
        if text_node == parent_node.text:
            children = list(parent_node)
            next_node = children[0] if children else None
        elif text_node == parent_node.tail:
            next_node = parent_node.getnext()   # next sibling or None

        # next resource is inside the current text
        if item_offset >= current_offset and item_end_offset <= text_end_offset:
            # text before the item: beginning of this node up to relative item offset
            text_before = normalized_text[:item_offset - current_offset]
            # text after the item: end item offset to end of text, relative to current offset
            text_after = normalized_text[item_end_offset - current_offset:]

            # special case: exact match on start and end offsets *and* the tag
            # matches the tag we would insert (i.e., detected name is already tagged)
            if item_offset == current_offset and item_end_offset == text_end_offset \
                and parent_node.tag[len(parent_node.prefix or ''):] == name_tag:
                # store the node so that attributes can be updated if not already set
                name_node = parent_node
                existing_tag = True

            else:
                existing_tag = False
                # update current text node with the text before the item
                if text_node == text_node.getparent().text:
                    text_node.getparent().text = text_before
                elif text_node == text_node.getparent().tail:
                    text_node.getparent().tail = text_before
                    # override the parent node: name tag should be inserted in the
                    # true parent node, not the preceding node
                    parent_node = parent_node.getparent()

                item_tag = node.makeelement(name_tag, nsmap=node.nsmap)
                # text content of the node is the recognized form of the name
                item_tag.text = item['surfaceForm']

                # if there is a node immediately after current text, insert new node before it
                if next_node is not None:
                    node_index = parent_node.index(next_node)
                    parent_node.insert(node_index, item_tag)
                # otherwise, just append at the end of the parent node
                else:
                    parent_node.append(item_tag)
                inserted += 1  # update item tag count

                last_node = item_tag

                if track_changes:
                    # create & insert oxygen processing instructions
                    # relative to the new node that was just inserted

                    # create a delete marker for the old text
                    oxy_delete = ProcessingInstruction('oxy_delete',
                        'author="namedropper" timestamp="%s" content="%s"' \
                        % (timestamp, item['surfaceForm']))
                    # FIXME: escape content in surface form (quotes, etc)

                    # create a marker for the beginning of an insertion
                    dbres = spotlight.DBpediaResource(item['URI'])
                    # use the description if possible, to provide enough
                    # context for reviewers to determine if this is the correct
                    # entity (other information doesn't seem to be useful
                    # or is already in the document in another form)
                    comment = dbres.description or dbres.label or \
                        '(label/description unavailable)'
                    oxy_insert_start = ProcessingInstruction('oxy_insert_start',
                        'author="namedropper" timestamp="%s"' % timestamp + \
                        ' comment="%s"' % comment)
                    # marker for the end of the insertion
                    oxy_insert_end = ProcessingInstruction('oxy_insert_end')

                    # - add deletion, then insertion start just before new tag
                    parent_node.insert(parent_node.index(item_tag), oxy_delete)
                    parent_node.insert(parent_node.index(item_tag), oxy_insert_start)
                    # - insert end *after* new tag
                    parent_node.insert(parent_node.index(item_tag) + 1,
                       oxy_insert_end)

                    # last pi is the one that will get the 'tail' text
                    last_node = oxy_insert_end

                name_node = item_tag

                # set text after the item to the "tail" text of the new item tag
                last_node.tail = text_after

                # set the remainder text as the next text node to be processed
                # - find via xpath so we have a "smart string" / lxml element string with getparent()
                remainder_node = last_node.xpath('./following-sibling::text()[1]')[0]

                text_list.insert(0, remainder_node)

            # add attributes to the name node (inserted or existing), but don't overwrite
            if mode == 'tei':
                attributes = {'ref': item['URI']}
                if tei_type:
                    attributes['type'] = tei_type
            elif mode == 'ead':
                name_tag = ead_tag

                # EAD can't reference dbpedia URI; lookup in VIAF
                attributes = {}
                if ead_tag == 'persname':
                    viaf_uri = get_viafid(item)
                    if viaf_uri:
                        viafid = viaf_uri.rstrip('/').rsplit('/', 1)[-1]
                        attributes = {'source': 'viaf', 'authfilenumber': viafid}
                    else:
                        logger.info('VIAF id not found for %s' % item['surfaceForm'])
                if ead_tag == 'geogname':
                    dbres = spotlight.DBpediaResource(item['URI'])
                    if dbres.geonames_id is not None:
                        attributes = {'source': 'geonames',
                            'authfilenumber': dbres.geonames_id}
                    else:
                        logger.info('GeoNames.org id not found for %s' % item['surfaceForm'])

                # for now, use dbpedia identifiers where no author id is available
                if not attributes:
                    # use unique identifier portion of dbpedia uri as id
                    base_uri, dbpedia_id = item['URI'].rsplit('/', 1)
                    attributes = {
                        'source': 'dbpedia',
                        'authfilenumber': dbpedia_id
                    }

            # set attributes on the newly inserted OR existing name tag
            added_attr = {}
            for attr, val in attributes.iteritems():
                current_val = name_node.get(attr, None)

                # add attribute values if they are not already set
                if current_val is None:
                    name_node.set(attr, val)
                    added_attr[attr] = val

                # Warn and do NOT set if attributes are present (and different)
                # FIXME: this may need some modification for EAD (since auth/source are a pair)
                elif current_val != val:
                    logger.warn('Not setting %s to %s because it already has a value of %s' %\
                        (attr, val, current_val))

            # if updating an existing node and track changes is requested
            # add a comment about the change
            if track_changes and existing_tag:
                # FIXME: comment 'author' should probably be a variable
                # TODO: comment text
                comment = ''
                if added_attr:
                    comment += 'Added attribute%s to existing %s tag: ' \
                     % ('s' if len(added_attr) != 1 else '',
                        name_node.xpath('local-name()')) + \
                        ', '.join('%s=%s' % (k, v) for k, v in added_attr.iteritems())

                if len(added_attr) != len(attributes):
                    comment += '\nDid not replace attribute%s: ' % \
                    ('s' if len(attributes) - len(added_attr) != 1 else '') + \
                    ', '.join('%s=%s with %s' % (k, name_node.get(k), v)
                        for k, v in attributes.iteritems() if k not in added_attr)
                oxy_comment_start = ProcessingInstruction('oxy_comment_start',
                    'author="namedropper" timestamp="%s"' % timestamp + \
                    ' comment="%s"' % comment)
                oxy_comment_end = ProcessingInstruction('oxy_comment_end')
                name_parent = name_node.getparent()
                name_parent.insert(name_parent.index(name_node),
                    oxy_comment_start)
                name_parent.insert(name_parent.index(name_node) + 1,
                    oxy_comment_end)
                # shift any tail text from name node to last pi
                oxy_comment_end.tail = name_node.tail
                name_node.tail = ''
                # next text node to process is the former name node tail text
                # replace it with the tail text shifted to the processing instruction
                text_list.pop(0)

                # duplicated from insertion logic...
                last_node = oxy_comment_end
                remainder_node = last_node.xpath('./following-sibling::text()[1]')[0]
                text_list.insert(0, remainder_node)
                #text_list.insert(0, oxy_comment_end.tail)

            # new current offset is the end of the last item
            current_offset = item_end_offset

            # clear item to indicate next one should be grabbed
            item = None

            # add current processed text to previous
            prev_text += text_before + item_tag.text

        # the next item is not inside the current text node
        # update offsets and previous text for the next loop,
        # still looking for the current item
        else:
            current_offset += len(normalized_text)
            # append the processed text to previous
            prev_text += normalized_text

    return inserted
