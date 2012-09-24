#!/usr/bin/env python

import unittest
from mock import patch, Mock

from namedropper.spotlight import SpotlightClient
from testcore import main


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

    def test_annotate(self, mockrequests):
        client = SpotlightClient()

        text = 'some bogus text to annotate'

        # simulate ok response
        mockrequests.post.return_value.status_code = 200
        mockrequests.codes.ok = 200
        mockrequests.post.return_value.json = self.sample_result
        result = client.annotate(text)

        self.assertEqual(client._clean_response(self.sample_result), result)

        post_headers = {
            'accept': 'application/json',
            'content-type': 'application/x-www-form-urlencoded'
        }

        mockrequests.post.assert_called_with(client.default_url + '/annotate',
            data={'text': text}, headers=post_headers)

        # TODO: simulate error

    # TODO: test _clean_response






if __name__ == '__main__':
    main()
