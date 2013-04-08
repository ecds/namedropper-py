# file namedropper-py/namedropper/spotlight.py
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

## spotlight.py

from datetime import datetime, timedelta
import logging
import rdflib
import requests
import time

from namedropper import viaf

logger = logging.getLogger(__name__)


# TODO: this should probably be split out into a submodule

# RDF namespaces
DBPPROP = rdflib.Namespace('http://dbpedia.org/property/')
DBPEDIA_OWL = rdflib.Namespace('http://dbpedia.org/ontology/')
GEO = rdflib.Namespace('http://www.w3.org/2003/01/geo/wgs84_pos#')
FOAF = rdflib.Namespace("http://xmlns.com/foaf/0.1/")
SCHEMA_ORG = rdflib.Namespace('http://schema.org/')
OWL = rdflib.Namespace('http://www.w3.org/2002/07/owl#')
':class:`rdflib.Namespace` for OWL (Web Ontology Language)'


class SpotlightClient(object):
    '''Client for interacting with DBpedia Spotlight via REST API.

    http://wiki.dbpedia.org/spotlight/usersmanual?v=ssd

    :param base_url: Base URL for DBpedia Spotlight webservice, when
        not using the hosted service at :attr:`default_url`
    :param confidence: default minimum confidence score (optional)
    :param support: default minimum support score (optional)
    :param types: list or string of default types to be returned
        when recognizing and annotating text

    '''

    default_url = 'http://spotlight.dbpedia.org/rest'
    'Default base url for DBpedia Spotlight web service'

    _api_calls = []
    # internal variable to keep track of number of queries & response time

    def __init__(self, base_url=None, confidence=None, support=None, types=None):
        if base_url is None:
            self.base_url = self.default_url
        else:
            self.base_url = base_url

        self.default_confidence = confidence
        self.default_support = support

        # support python list or string input
        if isinstance(types, list):
            types = ','.join(types)
        self.default_types = types

    def annotate(self, text, confidence=None, support=None, types=None):
        '''Call the DBpedia Spotlight ``annotate`` service.

        All arguments other than text are optional; if default configurations
        were specified when the client was initialized, those will be used
        unless an overriding value is specified here.

        :param text: text string to be annotated
        :param confidence: minimum confidence score (e.g., 0.5) [optional]
        :param support: minimum support score [optional]
        :param types: list or string of entity types that should
            be recognized and returned (such as Person, Place, Organization) [optional]

        :returns: dict with information on identified resources
        '''
        # types e.g., 'Person,Place'  or ['Person', 'Place']
        start = time.time()

        annotate_url = '%s/annotate' % self.base_url
        data = {'text': text}

        if confidence is not None:
            data['confidence'] = confidence
        elif self.default_confidence:
            data['confidence'] = self.default_confidence

        if support is not None:
            data['support'] = support
        elif self.default_support:
            data['support'] = self.default_support

        if types is not None:
            # if types is a list, convert to comma-delimited string
            if isinstance(types, list):
                types = ','.join(types)
            # otherwise, just pass as given
            data['types'] = types
        elif self.default_types:
            data['types'] = self.default_types

        rqst_args = {'headers': {'accept': 'application/json'}}

        # if text is less than some arbitrary size, use GET
        if len(text) < 5000:
            rqst_args['params'] = data
            rqst_method = requests.get

        # for longer text, use POST
        else:
            rqst_args['data'] = data
            rqst_args['headers']['content-type'] = 'application/x-www-form-urlencoded'
            rqst_method = requests.post

        response = self._call(rqst_method, annotate_url, **rqst_args)
        # # API docs suggest using POST instead of GET for large text content;
        # for POST, a content-type of application/x-www-form-urlencoded is required

        logger.debug('annotate \'%s...\': %s (%0.3f sec)' %
                     (text[:10], response.status_code, time.time() - start))

        if response.status_code == requests.codes.ok:
            return self._clean_response(response.json())

        # if response was not ok, raise the error
        response.raise_for_status()

    @property
    def total_api_calls(self):
        'number of API calls made'
        return len(self._api_calls)

    @property
    def total_api_duration(self):
        ':class:`datetime.timedelta` - total duration of all API calls'
        return sum(self._api_calls, timedelta())

    def _call(self, method, *args, **kwargs):
        # wrapper around request to allow keeping track of number
        # and duration of api calls
        start = datetime.now()
        result = method(*args, **kwargs)
        self._api_calls.append(datetime.now() - start)
        return result

    def _clean_response(self, data):
        '''Recursive function to clean up DBPedia Spotlight JSON result,
        which returns key names beginning with `@`.

        For a dictionary, return a new copy of the same dictionary, where '@' has been removed
        from keyds and value has been cleaned with :meth:`_clean_response`.  For a list, returns
        a list with every value cleaned by :meth:`_clean_response`.  Any other content is
        currently returned unchanged.
        '''
        if isinstance(data, dict):
            return dict((k.replace('@', ''),
                        self._clean_response(v)) for k, v in data.iteritems())
        elif isinstance(data, list):
            return [self._clean_response(i) for i in data]
        else:
            return data

        # NOTE: may not belong here, but somewhere: consider splitting out resource types
        # from comma-delimited string list into a python list


# TODO: fix decorator so docstrings work on decorated functions
# TODO: move to a common/utils location
def cached_property(f):
    """returns a cached property that is calculated by function f"""
    # from http://code.activestate.com/recipes/576563-cached-property/
    def get(self):
        try:
            return self._property_cache[f]
        except AttributeError:
            self._property_cache = {}
            x = self._property_cache[f] = f(self)
            return x
        except KeyError:
            x = self._property_cache[f] = f(self)
            return x

    return property(get)


# FIXME: maybe store on DBpediaResource class object?
_viaf_uris = {}
'''dictionary mapping dbpedia URIs to VIAF ids, to avoid repeat lookups
within the same session'''


class DBpediaResource(object):
    '''An object to encapsulate properties and functionality
    related to a specific dbpedia item.

    :param uri: dbpedia resource uri
    :param language: optional language code, for multilingual properties
       like label; defaults to 'en'
    :param spotlight_info: optional dictionary of data returned from
        spotlight annotation, to avoid unnecessary look-ups (e.g., for
        type of resource)
    '''

    # TODO: possibly add a mechanism to init from an annotation
    # result (pre-populate any values available from api result)

    _spotlight_types = []

    def __init__(self, uri, language='en', spotlight_info={}):
        self.uri = uri
        self.uriref = rdflib.URIRef(uri)
        base_url, self.id = uri.rsplit('/', 1)
        self.language = language

        # store any useful data from spotlight result
        if 'types' in spotlight_info:
            self._spotlight_types = spotlight_info['types'].split(',')
        # NOTE: if spotlight api adds other data (like label),
        # update to use that also

    @cached_property
    def graph(self):
        # NOTE: rdflib load uses HTTP_PROXY when it is set
        start = time.time()
        g = rdflib.graph.ConjunctiveGraph()
        g.load(self.uri)   # NOTE: not documented; actually calls parse
        logger.debug('Loaded RDF for %s (%0.3fs)' %
                    (self.uri, time.time() - start))
        # NOTE: this is fairly slow for some resources (e.g., places like
        # London or United States which include data about lots of people
        # associated with that place).
        # We could generate a graph with only the properties we need
        # via a targeted sparql query, but initial investigation indicates
        # that is significantly slower for the majority of our resources
        # (~1 second instead of ~0.1 second)

        return g

    @cached_property
    def label(self):
        '''preferred label for this resource, in current language'''
        results = self.graph.preferredLabel(
            self.uriref,
            lang=self.language)
        if results:
            return unicode(results[0][1])

    @cached_property
    def description(self):
        '''brief description of this resource in the current language'''
        for ab in self.graph.objects(self.uriref, rdflib.RDFS.comment):
            if ab.language == self.language:
                return ab

    def _graph_value(self, pred):
        # convenience method to get the value for a predicate
        try:
            return self.graph.value(subject=self.uriref,
                                    predicate=pred).toPython()
        except AttributeError:
            return None

    @cached_property
    def viafid(self):
        '''VIAF identifier for this resource (generally only available
            for persons, and not available for all persons)'''
        return self._graph_value(DBPPROP.viaf)

    @cached_property
    def viaf_uri(self):
        '''Search VIAF for a DBpedia resource to find the equivalent resource.
        Currently only supports Persons; uses the owl:sameAs relation in VIAF data
        to confirm that the correct resource has been found.

        :params resource: dict for a single dbpedia resource, as included in
            :meth:`namedropper.spotlight.SpotlightClient.annotate` results
            :returns: matching VIAF URI, or None if no match was found
        '''
        # if self.uri not in _viafids:
        #     viafid = None

        # use viafid property from dbpedia, if available
        if self.viafid:
            return 'http://viaf.org/viaf/%s' % self.viafid

        else:
            results = []
            # search for corresponding viaf resource by type

            if self.is_person:
                if self.uri in _viaf_uris:
                    return _viaf_uris[self.uri]

                # NOTE: only persons in VIAF have the dbpedia sameAs rel
                # For now, only implementing person-name VIAF lookup
                logger.info('VIAF id for %s not found in DBpedia; searching VIAF' %
                           (self.label))
                viafclient = viaf.ViafClient()
                results = viafclient.find_person(self.label)

                g = rdflib.Graph()

                # iterate through results and look for a result that has
                # an owl:sameAs relation to the dbpedia resource
                for result in results:
                    viaf_uriref = rdflib.URIRef(result['link'])
                    # load the RDF for the VIAF entity and parse a s an rdflib graph
                    g.parse(result['link'])
                    # check for the triple we're interested in
                    if (viaf_uriref, OWL['sameAs'], self.uriref) in g:
                        viaf_uri = result['link']
                        # store in case we need to look up again
                        _viaf_uris[self.uri] = viaf_uri
                        return viaf_uri

    #return _viafids.get(res.uri, None)

    @cached_property
    def geonames_uri(self):
        '''GeoNames URI for this resource (generally only available
            for places, and not available for all places)'''
        objects = self.graph.objects(subject=self.uriref, predicate=rdflib.OWL.sameAs)
        for obj in objects:
            if 'geonames.org' in unicode(obj):
                return unicode(obj)

    @cached_property
    def geonames_id(self):
        '''GeoNames numeric id for this resource (based on :prop:`geonames_uri`)'''
        if self.geonames_uri is not None:
            # strip off trailing slash, then split by slash and
            # return the last portion of the uri
            return self.geonames_uri.rstrip('/').rsplit('/', 1)[-1]

    @cached_property
    def thumbnail(self):
        '''thumbnail image for this resource'''
        return self._graph_value(DBPEDIA_OWL.thumbnail)

    @cached_property
    def latitude(self):
        'latitude (for places)'
        return self._graph_value(GEO.lat)

    @cached_property
    def longitude(self):
        'longitude (for places)'
        return self._graph_value(GEO.long)

    # RDF person types
    person_types = [FOAF.Person, DBPEDIA_OWL.Person, SCHEMA_ORG.Person]
    spotlight_person_types = ['DBpedia:Person', 'Schema:Person',
                              'Freebase:/people/person']

    @cached_property
    def is_person(self):
        'boolean flag to indicate if this resource represents a person'
        # here and for is_org/is_place, use types from spotlight result
        # when available, to avoid extra external requests
        if self._spotlight_types:
            return any(t in self._spotlight_types
                       for t in self.spotlight_person_types)

        return any(((self.uriref, rdflib.RDF.type, t) in self.graph
                    for t in self.person_types))

    # RDF org types
    org_types = [DBPEDIA_OWL.Organisation]
    spotlight_org_types = ['DBpedia:Organisation']

    @cached_property
    def is_org(self):
        '''boolean flag to indicate if this resource represents an
        organization or corporate group'''
        if self._spotlight_types:
            return any(t in self._spotlight_types
                       for t in self.spotlight_org_types)

        return any(((self.uriref, rdflib.RDF.type, t) in self.graph
                    for t in self.org_types))

    # RDF place types
    place_types = [DBPEDIA_OWL.Place]
    spotlight_place_types = ['DBpedia:Place']

    @cached_property
    def is_place(self):
        'boolean flag to indicate if this resource represents a place'
        if self._spotlight_types:
            return any(t in self._spotlight_types
                       for t in self.spotlight_place_types)
        return any(((self.uriref, rdflib.RDF.type, t) in self.graph
                   for t in self.place_types))

    @property
    def type(self):
        '''high-level type of resource; currently only supports person,
        place, and organization.'''
        if self.is_person:
            return 'Person'
        if self.is_place:
            return 'Place'
        if self.is_org:
            return 'Organization'
        else:
            return ''
