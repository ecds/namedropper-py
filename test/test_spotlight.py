# file namedropper-py/test/test_spotlight.py
# coding=utf-8
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

import os.path
import rdflib

import unittest
from mock import patch

from namedropper.spotlight import SpotlightClient, DBpediaResource


@patch('namedropper.spotlight.requests')
class SpotlightClientTest(unittest.TestCase):
    sample_result = {
        "@text": "Hobsbaum spent the remainder of his teaching career at the University of Glasgow. From 1966 to 1985 he was a lecturer and reader before being promoted to Professor of English Literature in 1985. He married his second wife Rosemary Philips in 1976. In addition to his teaching and writing duties, Hobsbaum began the masters program in creative writing at the University of Glasgow. He retired from teaching in 1997. He has four published collections of poetry: The Place's Fault (1964), In Retreat (1966), Coming Out Fighting (1969), and Women and Animals (1972). Hobsbaum has also published two works of literary criticism.",
        "@confidence": "0.4",
        "@support": "20",
        "@types": "Person",
        "@sparql": "",
        "@policy": "whitelist",
        "Resources": [{
            "@URI": "http://dbpedia.org/resource/Edgar_Lee_Masters",
            "@support": "98",
            "@types": "DBpedia:Writer,DBpedia:Artist,DBpedia:Person,Schema:Person,Freebase:/book/author,Freebase:/book,Freebase:/award/award_winner,Freebase:/award,Freebase:/people/deceased_person,Freebase:/people,Freebase:/award/award_nominee,Freebase:/people/person",
            "@surfaceForm": "masters",
            "@offset": "315",
            "@similarityScore": "0.171113520860672",
            "@percentageOfSecondRank": "0.6365209051735774"
        }]
    }

    def test_init(self, mockrequests):
        # all default options
        client = SpotlightClient()
        self.assertEqual(client.default_url, client.base_url)

        # all custom options
        base_url = 'http://my.spotlight.org/mirror/'
        confidence = 0.2
        support = 42
        types = ['Person', 'Place']
        client = SpotlightClient(base_url,
            confidence=confidence, support=support,
            types=types)
        self.assertEqual(base_url, client.base_url)
        self.assertEqual(confidence, client.default_confidence)
        self.assertEqual(support, client.default_support)
        self.assertEqual(','.join(types), client.default_types)

    def test_clean_response(self, mockrequests):
        client = SpotlightClient()
        cleaned_data = client._clean_response(self.sample_result)

        self.assert_('text' in cleaned_data)
        self.assert_('@text' not in cleaned_data)
        self.assert_('types' in cleaned_data)
        self.assert_('@types' not in cleaned_data)
        self.assert_('URI' in cleaned_data['Resources'][0])
        self.assert_('@support' not in cleaned_data['Resources'][0])

    def test_annotate(self, mockrequests):
        client = SpotlightClient()

        text = 'some bogus text to annotate'

        # simulate ok response
        mockrequests.get.return_value.status_code = 200
        mockrequests.codes.ok = 200
        mockrequests.get.return_value.json.return_value = self.sample_result
        result = client.annotate(text)

        self.assertEqual(client._clean_response(self.sample_result), result)

        get_headers = {
            'accept': 'application/json',
            #'content-type': 'application/x-www-form-urlencoded'
        }

        mockrequests.get.assert_called_with(client.default_url + '/annotate',
            params={'text': text}, headers=get_headers)

        # TODO: test larger text / post

        # TODO: simulate error


class DBpediaResourceTest(unittest.TestCase):
    URI = {
        'heaney': 'http://dbpedia.org/resource/Seamus_Heaney',
        'belfast': 'http://dbpedia.org/resource/Belfast'
    }

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    FIXTURES = {
        'heaney': os.path.join(BASE_DIR, 'fixtures', 'Seamus_Heaney.rdf'),
        'belfast': os.path.join(BASE_DIR, 'fixtures', 'belfast.rdf'),
    }

    SPOTLIGHT_INFO = {
        "URI": "http://dbpedia.org/resource/Edgar_Lee_Masters",
        "support": "98",
        "types": "DBpedia:Writer,DBpedia:Artist,DBpedia:Person,Schema:Person,Freebase:/book/author,Freebase:/book,Freebase:/award/award_winner,Freebase:/award,Freebase:/people/deceased_person,Freebase:/people,Freebase:/award/award_nominee,Freebase:/people/person",
        "surfaceForm": "masters",
        "offset": "315",
        "similarityScore": "0.171113520860672",
        "percentageOfSecondRank": "0.6365209051735774"
    }

    def test_init(self):
        res = DBpediaResource(self.URI['heaney'])
        self.assertEqual(self.URI['heaney'], res.uri)
        self.assertEqual(rdflib.URIRef(self.URI['heaney']), res.uriref)
        self.assertEqual('Seamus_Heaney', res.id)
        self.assertEqual('en', res.language)

        res = DBpediaResource(self.URI['heaney'], 'ja')
        self.assertEqual('ja', res.language)

        # test init with spotlight info
        with patch('namedropper.spotlight.rdflib') as mockrdflib:
            res = DBpediaResource(self.SPOTLIGHT_INFO['URI'],
                                  spotlight_info=self.SPOTLIGHT_INFO)
            self.assertEqual(True, res.is_person)
            self.assert_(not mockrdflib.graph.ConjunctiveGraph.called,
                         'rdflib.graph should not be loaded when ' +
                         'types are available via spotlight info')

    def test_rdf_properties(self):
        g = rdflib.graph.Graph()
        g.load(self.FIXTURES['heaney'])

        # patch in local fixture to avoid hitting dbpedia
        with patch.object(DBpediaResource, 'graph', new=g):
            sh = DBpediaResource(self.URI['heaney'])
            self.assertEqual('Seamus Heaney', sh.label)
            self.assertEqual(109557338, sh.viafid)
            self.assertEqual(None, sh.latitude)
            self.assertEqual(None, sh.longitude)
            self.assertEqual(True, sh.is_person)
            # beginning of english rdfs:comment
            en_desc = 'Seamus Heaney is an Irish poet, playwright, translator,'
            self.assert_(sh.description.startswith(en_desc))

            sh = DBpediaResource(self.URI['heaney'], 'ja')
            self.assertNotEqual('Seamus Heaney', sh.label)

            # beginning of french rdfs:comment
            fr_desc = u'Seamus Heaney est un poète irlandais'
            sh = DBpediaResource(self.URI['heaney'], 'fr')
            self.assert_(sh.description.startswith(fr_desc))

            # non-place should not error but return none for geonames
            self.assertEqual(None, sh.geonames_uri)
            self.assertEqual(None, sh.geonames_id)

        g.load(self.FIXTURES['belfast'])
        with patch.object(DBpediaResource, 'graph', new=g):
            sh = DBpediaResource(self.URI['belfast'])
            self.assertEqual('Belfast', sh.label)
            self.assertEqual(None, sh.viafid)
            self.assertAlmostEqual(54.596, sh.latitude, places=2)
            self.assertAlmostEqual(-5.930, sh.longitude, places=2)
            self.assertEqual(False, sh.is_person)

            self.assertEqual('http://sws.geonames.org/3333223/',
                sh.geonames_uri)
            self.assertEqual('3333223', sh.geonames_id)

