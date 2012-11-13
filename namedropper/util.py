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

import logging
from lxml.etree import XMLSyntaxError, parse
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


def get_viafid(resource):
    '''Search VIAF for a DBpedia resource to find the equivalent resource.
    Currently only supports Persons; uses the owl:sameAs relation in VIAF data
    to confirm that the correct resource has been found.

    :params resource: dict for a single dbpedia resource, as included in
        :meth:`namedropper.spotlight.SpotlightClient.annotate` results
    :returns: matching VIAF URI, or None if no match was found
    '''
    uri = resource['URI']
    if uri not in _viafids:
        viafid = None
        viafclient = viaf.ViafClient()

        # if we haven't already done so, check for viaf id in dbpedia first
        if uri not in _dbpedia_viaf_lookups:
            _dbpedia_viaf_lookups.append(uri)
            viafid = spotlight.dbpedia_viafid(uri)
            if viafid:
                # store url format, for consistency with viaf search results
                _viafids[uri] = 'http://viaf.org/viaf/%s' % viafid

        # if viaf id was not found in dbpedia, use viaf search
        if not viafid:
            # determine type of resource
            rsrc_type = None
            if 'DBpedia:Person' in resource['types']:
                rsrc_type = 'person'
            # elif 'DBpedia:Place' in resource['types']:
            #     rsrc_type = 'place'
            # elif 'DBpedia:Organisation' in resource['types']:
            #     rsrc_type = 'corp'

            label = spotlight.dbpedia_label(uri)
            # TODO: fall-back label? what should this actually do here?
            if not label:
                return None

            results = []
            # search for corresponding viaf resource by type
            if rsrc_type == 'person':
                results = viafclient.find_person(label)

            # NOTE: only persons in VIAF have the dbpedia sameAs rel
            # How to reliably link places and organizations?
            # For now, only implementing person-name VIAF lookup

            # elif rsrc_type == 'place':
            #     results = viaf.find_place(label)
            # elif rsrc_type == 'corp':
            #     results = viaf.find_corporate(label)

            g = Graph()
            dbpedia_uriref = URIRef(uri)

            # iterate through results and look for a result that has
            # an owl:sameAs relation to the dbpedia resource
            for result in results:
                viaf_uriref = URIRef(result['link'])
                # load the RDF for the VIAF entity and parse as an rdflib graph
                g.parse(result['link'])
                # check for the triple we're interested in
                if (viaf_uriref, OWL['sameAs'], dbpedia_uriref) in g:
                    viafid = result['link']
                    _viafids[uri] = viafid
                    break

    return _viafids.get(uri, None)


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


def annotate_xml(node, result, mode='tei'):
    '''Annotate xml based on dbpedia spotlight annotation results.  Assumes
    that dbpedia annotate was called on the **normalized** text from this node.
    Currently updates the node that is passed in; whitespace will be normalized in text
    nodes where name tags are inserted.

    :param node: lxml element node to be updated
    :param result: dbpedia spotlight result, as returned by
        :meth:`namedropper.spotlight.SpotlightClient.annotate`

    :returns: total count of the number of entities inserted into the xml
    '''

    # TEI tags for now
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

    # iterate until we run out of text nodes or resources
    while (item or resources) and text_list:
        # if there is no current item, get the next item
        if item is None:
            item = resources.pop(0)
            item_offset = int(item['offset'])
            item_end_offset = item_offset + len(item['surfaceForm'])

            # determine tag name to be used for this item
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

        # special case - exact match (i.e., the detected name is already tagged)
        if item_offset == current_offset and item_end_offset == text_end_offset \
            and parent_node.tag[len(parent_node.prefix or ''):] == name_tag:
            # update attributes if not already set; otherwise, warn
            # about the info that is not being saved to avoid overwriting existing data

            # TODO: redundant logic; consolidate with new tag attribute logic below
            if mode == 'tei':
                ref = parent_node.get('ref', None)
                # if no ref attribute is present, add one
                if ref is None:
                    parent_node['ref'] = item['URI']
                # if already set and different to the new value, warn
                elif item['URI'] != ref:
                    logger.warn('Not setting ref to %s because it is already set as %' \
                        % (item['URI'], ref))

                if parent_node.get('type', None) is None:
                    parent_node['type'] = tei_type
                # not warning if type is already set; seems less crucial than losing the URI

            elif mode == 'ead' and name_tag == 'persname':
                # NOTE: currently only support viaf lookup for persname
                src = parent_node.get('source', None)
                authnumber = parent_node.get('authfilenumber', None)
                if src is not None and authnumber is not None:
                    viafid = get_viafid(item)
                    if viafid:
                        parent_node['source'] = 'viaf'
                        parent_node['authfilenumber'] = viafid
                        attributes = {'source': 'viaf', 'authfilenumber': viafid}
                    else:
                        logger.info('VIAF id not found for %s' % item['surfaceForm'])
                else:
                    logger.warn('Not looking up VIAF id because source or authfilenumber for %s is already set' \
                        % item['surfaceForm'])

            # new current offset is the end of the last item
            current_offset = item_end_offset

            # clear item to indicate next one should be grabbed
            item = None
            # add current processed text to previous
            prev_text += parent_node.text

        # next resource is inside the current text
        elif item_offset >= current_offset and item_end_offset <= text_end_offset:
            # text before the item: beginning of this node up to relative item offset
            text_before = normalized_text[:item_offset - current_offset]
            # text after the item: end item offset to end of text, relative to current offset
            text_after = normalized_text[item_end_offset - current_offset:]

            # update current text node with the text before the item
            if text_node == text_node.getparent().text:
                text_node.getparent().text = text_before
            elif text_node == text_node.getparent().tail:
                text_node.getparent().tail = text_before
                # override the parent node: name tag should be inserted in the
                # true parent node, not the preceding node
                parent_node = parent_node.getparent()

            if mode == 'tei':
                attributes = {'ref': item['URI']}
                if tei_type:
                    attributes['type'] = tei_type
            elif mode == 'ead':
                name_tag = ead_tag
                # create the new node in the same namespace as its parent
                if node.nsmap and node.prefix in node.nsmap:
                    name_tag = '{%s}%s' % (node.nsmap[node.prefix], ead_tag)

                # EAD can't reference dbpedia URI; lookup in VIAF
                attributes = {}
                if ead_tag == 'persname':
                    viafid = get_viafid(item)
                    if viafid:
                        attributes = {'source': 'viaf', 'authfilenumber': viafid}
                    else:
                        logger.info('VIAF id not found for %s' % item['surfaceForm'])

            item_tag = node.makeelement(name_tag, attrib=attributes,
                nsmap=node.nsmap)
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

            # new current offset is the end of the last item
            current_offset = item_end_offset

            # clear item to indicate next one should be grabbed
            item = None
            # set text after the item to the "tail" text of the new item tag
            item_tag.tail = text_after

            # set the remainder text as the next text node to be processed
            # - find via xpath so we have a "smart string" / lxml element string with getparent()
            remainder_node = item_tag.xpath('./following-sibling::text()[1]')[0]

            text_list.insert(0, remainder_node)
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
