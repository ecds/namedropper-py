#!/usr/bin/env python

# file namedropper-py/test/test_util.py
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

import unittest
import os
from eulxml.xmlmap import load_xmlobject_from_file
#from eulxml.xmlmap.eadmap import EncodedArchivalDescription as EAD
from eulxml.xmlmap.teimap import Tei, TEI_NAMESPACE

from namedropper.util import autodetect_file_type, annotate_xml, is_person, is_place
from testcore import main
from fixtures import ilnnames_annotations

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

FIXTURES = {
    'tei': os.path.join(BASE_DIR, 'fixtures', 'ILNnamesTestSample.xml'),
    'ead': os.path.join(BASE_DIR, 'fixtures', 'hobsbaum1013.xml'),
    'text': os.path.join(BASE_DIR, 'fixtures', 'longley-bio.txt'),
    'generic-xml': os.path.join(BASE_DIR, 'fixtures', 'longley-bio.xml')
}


class AutodetectFileTypeTest(unittest.TestCase):

    def test_autodetect_file_type(self):
        self.assertEqual('tei', autodetect_file_type(FIXTURES['tei']))
        self.assertEqual('ead', autodetect_file_type(FIXTURES['ead']))
        self.assertEqual('text', autodetect_file_type(FIXTURES['text']))
        self.assertEqual(None, autodetect_file_type(FIXTURES['generic-xml']))

# TODO: should test get_viafid
# (will probably require significant mock / fixtures to avoid hitting VIAF )


class AnnotateXmlTest(unittest.TestCase):

    tei_ns = {'namespaces': {'t': TEI_NAMESPACE}}

    def setUp(self):
        self.tei = load_xmlobject_from_file(FIXTURES['tei'], Tei)

    def test_annotate_xml__simplest(self):
        # simplest case: article with a single paragraph and no mixed content or nested tags
        annotations = ilnnames_annotations.article3_result
        nodelist = self.tei.node.xpath('//t:div2[@xml:id="iln42.1183.005"]/t:p', **self.tei_ns)
        article3 = nodelist[0]
        text_content = article3.xpath('normalize-space(.)')
        inserted = annotate_xml(article3, annotations)

        # normalized text should be the same before and after
        self.assertEqual(text_content, article3.xpath('normalize-space(.)'))
        names = article3.xpath('t:name', **self.tei_ns)

        # inspect the tags that were inserted
        self.assertEqual(len(annotations['Resources']), len(names),
            'number of resources identified in dbpedia spotlight result should be tagged in the xml')
        self.assertEqual(len(annotations['Resources']), inserted,
            'resources identified in spotlight result should match reported inserted count')
        # both resources are places; uri & value should match equivalent dbpedia result
        for i in [0, 1]:
            result = annotations['Resources'][i]
            self.assertEqual('place', names[i].get('type'))
            # uri & value should match dbpedia result
            self.assertEqual(result['URI'], names[i].get('res'))
            self.assertEqual(result['surfaceForm'], names[i].text)

    def test_annotate_xml__end_tag(self):
        # slightly less simple case - single paragraph article with one nested tag near the end
        annotations = ilnnames_annotations.article1_result
        article = self.tei.node.xpath('//t:div2[@xml:id="iln42.1182.003"]/t:p', **self.tei_ns)[0]
        text_content = article.xpath('normalize-space(.)')
        hi_rend_text = ''.join(article.xpath('t:hi//text()', **self.tei_ns))
        inserted = annotate_xml(article, annotations)

        # normalized text should be the same before and after
        self.assertEqual(text_content, article.xpath('normalize-space(.)'))

        # inspect the tags that were inserted
        names = article.xpath('.//t:name', **self.tei_ns)
        self.assertEqual(len(annotations['Resources']), len(names),
            'the number of resources in the dbpedia spotlight result should match the names tagged in the xml')
        self.assertEqual(len(annotations['Resources']), inserted,
            'resources identified in spotlight result should match reported inserted count')
        new_hi_rend_text = ''.join(article.xpath('t:hi//text()', **self.tei_ns))
        self.assertEqual(hi_rend_text, new_hi_rend_text)
        # as before, all resources are places; uri & value should match equivalent dbpedia result
        for i in [0, 1]:
            result = annotations['Resources'][i]
            self.assertEqual('place', names[i].get('type'))
            # uri & value should match dbpedia result
            self.assertEqual(result['URI'], names[i].get('res'))
            self.assertEqual(result['surfaceForm'], names[i].text)

    def test_annotate_xml__mid_tag(self):
        # second article - single paragraph with a nested tag in the middle
        # - nested tag contains recognized entities
        annotations = ilnnames_annotations.article2_result
        article = self.tei.node.xpath('//t:div2[@xml:id="iln42.1182.005"]/t:p', **self.tei_ns)[0]
        text_content = article.xpath('normalize-space(.)')
        hi_rend_text = ''.join(article.xpath('t:hi//text()', **self.tei_ns))
        inserted = annotate_xml(article, annotations)

        # normalized text should be the same before and after
        self.assertEqual(text_content, article.xpath('normalize-space(.)'))
        new_hi_rend_text = ''.join(article.xpath('t:hi//text()', **self.tei_ns))
        self.assertEqual(hi_rend_text, new_hi_rend_text)

        # inspect the tags that were inserted
        names = article.xpath('.//t:name', **self.tei_ns)
        self.assertEqual(len(annotations['Resources']), len(names),
            'the number of resources in the dbpedia spotlight result should match the names tagged in the xml')
        self.assertEqual(len(annotations['Resources']), inserted,
            'resources identified in spotlight result should match reported inserted count')
        # as before, all resources are places; uri & value should match equivalent dbpedia result
        for i in [0, 1]:
            result = annotations['Resources'][i]
            if is_person(result):
                self.assertEqual('person', names[i].get('type'))
            elif is_place(result):
                self.assertEqual('place', names[i].get('type'))
            # uri & value should match dbpedia result
            self.assertEqual(result['URI'], names[i].get('res'))
            self.assertEqual(result['surfaceForm'], names[i].text)

    def test_annotate_xml__empty_mid_tag(self):
        # article with a nested tag with no recognized entities
        #  ( - manufactured example based on article 3)

        annotations = ilnnames_annotations.article3_result
        nodelist = self.tei.node.xpath('//t:div2[@xml:id="iln42.1183.005a"]/t:p', **self.tei_ns)
        article3 = nodelist[0]
        text_content = article3.xpath('normalize-space(.)')
        inserted = annotate_xml(article3, annotations)

        # normalized text should be the same before and after
        self.assertEqual(text_content, article3.xpath('normalize-space(.)'))
        names = article3.xpath('t:name', **self.tei_ns)

        # inspect the tags that were inserted
        self.assertEqual(len(annotations['Resources']), len(names),
            'resources identified in dbpedia spotlight result should be tagged in the xml')
        self.assertEqual(len(annotations['Resources']), inserted,
            'resources identified in spotlight result should match reported inserted count')
        # both resources are places; uri & value should match equivalent dbpedia result
        for i in [0, 1]:
            result = annotations['Resources'][i]
            self.assertEqual('place', names[i].get('type'))
            # uri & value should match dbpedia result
            self.assertEqual(result['URI'], names[i].get('res'))
            self.assertEqual(result['surfaceForm'], names[i].text)

    def test_annotate_xml__start_tag(self):
        # article with a tag at the beginning

        annotations = ilnnames_annotations.article3_result
        nodelist = self.tei.node.xpath('//t:div2[@xml:id="iln42.1183.005b"]/t:p', **self.tei_ns)
        article3 = nodelist[0]
        text_content = article3.xpath('normalize-space(.)')
        inserted = annotate_xml(article3, annotations)

        # normalized text should be the same before and after
        self.assertEqual(text_content, article3.xpath('normalize-space(.)'))
        names = article3.xpath('t:name', **self.tei_ns)

        # inspect the tags that were inserted
        self.assertEqual(len(annotations['Resources']), len(names),
            'resources identified in dbpedia spotlight result should be tagged in the xml')
        self.assertEqual(len(annotations['Resources']), inserted,
            'resources identified in spotlight result should match reported inserted count')
        # both resources are places; uri & value should match equivalent dbpedia result
        for i in [0, 1]:
            result = annotations['Resources'][i]
            self.assertEqual('place', names[i].get('type'))
            # uri & value should match dbpedia result
            self.assertEqual(result['URI'], names[i].get('res'))
            self.assertEqual(result['surfaceForm'], names[i].text)

    def test_annotate_xml__multiple_nested(self):
        # article with multiple entities in a single nested subelement

        annotations = ilnnames_annotations.article3_result
        nodelist = self.tei.node.xpath('//t:div2[@xml:id="iln42.1183.005c"]/t:p', **self.tei_ns)
        article3 = nodelist[0]
        text_content = article3.xpath('normalize-space(.)')
        inserted = annotate_xml(article3, annotations)

        # normalized text should be the same before and after
        self.assertEqual(text_content, article3.xpath('normalize-space(.)'))
        names = article3.xpath('.//t:name', **self.tei_ns)

        # inspect the tags that were inserted
        self.assertEqual(len(annotations['Resources']), len(names),
            'resources identified in dbpedia spotlight result should be tagged in the xml')
        self.assertEqual(len(annotations['Resources']), inserted,
            'resources identified in spotlight result should match reported inserted count')
        # both resources are places; uri & value should match equivalent dbpedia result
        for i in [0, 1]:
            result = annotations['Resources'][i]
            self.assertEqual('place', names[i].get('type'))
            # uri & value should match dbpedia result
            self.assertEqual(result['URI'], names[i].get('res'))
            self.assertEqual(result['surfaceForm'], names[i].text)

    def test_annotate_xml__with_bibl(self):
        # article with full bibliography / header; processing at div2 level instead of paragraph
        annotations = ilnnames_annotations.article4_result
        article = self.tei.node.xpath('//t:div2[@xml:id="iln38.1069.006"]', **self.tei_ns)[0]
        text_content = article.xpath('normalize-space(.)')
        inserted = annotate_xml(article, annotations)

        names = article.xpath('.//t:name', **self.tei_ns)

        # inspect the tags that were inserted
        expected = len(annotations['Resources'])
        got = len(names)
        self.assertEqual(expected, got,
            'resources identified in dbpedia spotlight result should be tagged in the xml (expected %d, got %d)' \
            % (expected, got))
        self.assertEqual(len(annotations['Resources']), inserted,
            'resources identified in spotlight result should match reported inserted count')

        # normalized text should be the same before and after
        self.assertEqual(text_content, article.xpath('normalize-space(.)'))

        # both resources are places; uri & value should match equivalent dbpedia result
        for i in [0, 1]:
            result = annotations['Resources'][i]
            self.assertEqual('place', names[i].get('type'))
            # uri & value should match dbpedia result
            self.assertEqual(result['URI'], names[i].get('res'))
            self.assertEqual(result['surfaceForm'], names[i].text)


if __name__ == '__main__':
    main()

