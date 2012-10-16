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

