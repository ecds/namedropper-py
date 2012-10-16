# file namedropper-py/namedropper/viaf.py
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


import requests
import feedparser


class ViafClient(object):
    '''Client for interacting with `VIAF`_ (Virtual International Authority File) API.

    .. _VIAF: http://viaf.org


    http://www.oclc.org/developer/documentation/virtual-international-authority-file-viaf/using-api
    '''

    base_url = 'http://viaf.org/'

    def autosuggest(self, term):
        'Query autosuggest API.  Returns a list of results.'
        #    'viaf/AutoSuggest?query=[searchTerms]&callback[optionalCallbackName]
        autosuggest_url = '%s/viaf/AutoSuggest' % self.base_url
        response = requests.get(autosuggest_url, params={'query': term},
            headers={'accept': 'application/json'})
        if response.status_code == requests.codes.ok:
            return response.json['result']

        # if response was not ok, raise the error
        response.raise_for_status()

    # TODO: create separate person/place/corp name search methods/modes

    def search(self, query):
        '''Query VIAF seach interface.  Returns a list of feed entries, as
        parsed by :mod:`feedparser`.

        :param query: CQL query in viaf syntax (e.g., ``cql.any all "term"``)

        '''
        search_url = '%s/viaf/search' % self.base_url
        # local.names ?
        params = {
            'query': query,
            'httpAccept': 'application/rss+xml',
            'maximumRecords': 100,   # TODO: param?
            'sortKeys': 'holdingscount'  # default sort on web search...
            }

        response = requests.get(search_url, params=params)
        if response.status_code == requests.codes.ok:
            feed_data = feedparser.parse(response.content)
            return feed_data.entries

        # if response was not ok, raise the error
        response.raise_for_status()

    def _find_type(self, filter, value):
        return self.search('%s all "%s"' % (filter, value))

    def find_person(self, name):
        'Search VIAF by local.personalNames'
        return self._find_type('local.personalNames', name)

    def find_corporate(self, name):
        'Search VIAF by local.corporateNames'
        return self._find_type('local.corporateNames', name)

    def find_place(self, name):
        'Search VIAF by local.geographicNames'
        return self._find_type('local.geographicNames', name)


