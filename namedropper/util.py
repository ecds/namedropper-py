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


def annotate_xml(node, result, initial_offset=0, end_offset=None):
    '''Annotate xml based on dbpedia spotlight annotation results.  Assumes
    that dbpedia annotate was called on the **normalized** text from this node.

    :param node: lxml element node
    :param result: dbpedia spotlight result, as returned by
        :meth:`namedropper.spotlight.SpotlightClient.annotate`
    :param initial_offset: start annotating the xml at the requested offset;
        should only be used when called recursively  (adjust result offsets
        relative to the offset of a sub element)
    :param end_offset: end offset where annotation should stop; should only
        be used when called recursively (stop processing after
        finishing the content for a sub elemen)
    '''
    # very crude initial stab; assumes single node with untagged text
    # assuming TEI tags for now

    name_tag = 'name'
    # create the new node in the same namespace as its parent
    if node.nsmap and node.prefix in node.nsmap:
        name_tag = '{%s}%s' % (node.nsmap[node.prefix], name_tag)

    cur_offset = 0
    # TODO: copy node rather than changing original passed in?
    orig_node_text = node.xpath('normalize-space(text())')
    # capture the original text of this node before we modify it;
    # whitespace normalized to match the normalized text given to dbpedia

    # clear out the existing text in the lxml node we will be annotating
    node.text = None
    # grab the text relative to the requested initial offset
    # (identified resources will be offset relative to this text)
    txt = result['text'][initial_offset:]

    # iterate through resources and add text + tags for resources
    index = 0
    for item in result['Resources']:
        # convert string offset to int
        item_offset = int(item['offset']) - initial_offset
        if end_offset and item_offset > end_offset:
            # end offset indicates node is a sub element

            # break out of for loop, but don't return without handling
            # any remainder/tail text after the last resource
            break

        if item_offset >= len(orig_node_text):
            # get the node *after* the last inserted name
            next_node = node.getchildren()[index]

            # insert the remainder of original text on tail
            remainder = orig_node_text[cur_offset:]
            # update the current offset
            cur_offset += len(remainder)

            # NOTE: because we are using normalize-whitespace, there could be
            # a whitespace discrepancy here.  Check if the character immediately
            # after remaindex content is a space; if the next node text does NOT starts with
            # a space, assuming that the space should be included in the remainder tail text here.
            if txt[cur_offset:cur_offset + 1] == ' ':
                if not next_node.text.startswith(' '):   # TODO: handle nested text
                    remainder += ' '
                    cur_offset += 1
            node.getchildren()[index - 1].tail = remainder

            next_node_text = next_node.xpath('normalize-space(.)')
            # if the next name falls within next node text, recurse and tag names
            # - check that offset and surface form length are *both* inside the range of this node
            if item_offset >= cur_offset and \
                item_offset + len(item['surfaceForm']) < cur_offset + len(next_node_text):

                # make a copy of the spotlight result data
                result_copy = result.copy()
                result_copy['Resources'] = result['Resources'][index:]
                # annotate the node and adjust offset
                annotate_xml(next_node, result_copy, initial_offset=cur_offset, end_offset=len(next_node_text))
                cur_offset += len(next_node_text)

                orig_node_text = ''.join([orig_node_text, next_node_text, next_node.tail or ''])

                # this resource has been handled; update node index and go to next item

                index += 1

                # FIXME
                #print 'index is ', index
                #print [orig_node_text, next_node_text, next_node.tail or '']

                continue

            # in theory, item could straddle item tags; probably just report & skip
            # since that's probably not something we can handle automatically

            # TODO: warn & skip if item straddles a node

        # replace existing text node with text up to first recognized item
        if node.text is None and cur_offset == 0:
            node.text = txt[cur_offset:item_offset]
        else:
            # put text up to next offset on the tail of the last inserted node
            node.getchildren()[index - 1].tail = txt[cur_offset:item_offset]

        if is_person(item):
            name_type = 'person'
        elif is_org(item):
            name_type = 'org'
        elif is_place(item):
            name_type = 'place'

        item_tag = node.makeelement(name_tag, attrib={'res': item['URI'], 'type': name_type},
            nsmap=node.nsmap)
        item_tag.text = item['surfaceForm']

        cur_offset = item_offset + len(item['surfaceForm'])
        #node.append(item_tag)
        # insert at the current index, to avoid conflicts with any existing child nodes
        node.insert(index, item_tag)
        index += 1

    # append any trailing text after the last entity, up to the requested end offset
    if cur_offset < len(txt):
        childnodes = node.getchildren()
        remainder = txt[cur_offset:end_offset]
        if childnodes:
            childnodes[-1].tail = remainder
        else:
            node.text = remainder


def is_person(item):
    item_types = [i.strip() for i in item['types'].split(',')]
    return 'DBpedia:Person' in item_types or 'Freebase:/people/person' in item_types


def is_org(item):
    item_types = [i.strip() for i in item['types'].split(',')]
    return 'DBpedia:Organisation' in item_types


def is_place(item):
    item_types = [i.strip() for i in item['types'].split(',')]
    return 'DBpedia:Place' in item_types

