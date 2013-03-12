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

from copy import deepcopy
import unittest
import os
from eulxml.xmlmap import load_xmlobject_from_file
from eulxml.xmlmap.eadmap import EncodedArchivalDescription as EAD, EAD_NAMESPACE
from eulxml.xmlmap.teimap import Tei, TEI_NAMESPACE
from mock import patch, Mock

from namedropper import spotlight
from namedropper.util import autodetect_file_type, annotate_xml, \
    AnnotateXml
from fixtures import ilnnames_annotations, hobsbaum_annotations

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
    ead_ns = {'namespaces': {'e': EAD_NAMESPACE}}

    def setUp(self):
        self.tei = load_xmlobject_from_file(FIXTURES['tei'], Tei)
        self.ead = load_xmlobject_from_file(FIXTURES['ead'], EAD)

        self.tei_annotater = AnnotateXml('tei')
        self.ead_annotater = AnnotateXml('ead')

    def test_tag(self):
        rsrc = Mock(spec=spotlight.DBpediaResource)

        # TEI
        # (doesn't actually matter what type of resource)
        self.assertEqual('name', self.tei_annotater.get_tag(rsrc))

        # EAD
        # - person
        rsrc.is_person = True
        self.assertEqual('persname', self.ead_annotater.get_tag(rsrc))
        # - corporate/organization
        rsrc.is_person = False
        rsrc.is_org = True
        self.assertEqual('corpname', self.ead_annotater.get_tag(rsrc))
        # - geographical/place name
        rsrc.is_org = False
        rsrc.is_place = True
        self.assertEqual('geogname', self.ead_annotater.get_tag(rsrc))

        # set current node to inherit namespace
        self.tei_annotater.current_node = self.tei.node
        self.ead_annotater.current_node = self.ead.node
        self.assertEqual('{%s}name' % TEI_NAMESPACE,
                         self.tei_annotater.get_tag(rsrc))
        self.assertEqual('{%s}geogname' % EAD_NAMESPACE,
                         self.ead_annotater.get_tag(rsrc))

    def test_attributes(self):
        rsrc = Mock(spec=spotlight.DBpediaResource)
        rsrc.uri = 'http://dbpedia.org/resource/TestResource'

        # TEI
        # - person
        rsrc.is_person = True
        attr = self.tei_annotater.get_attributes(rsrc)
        self.assertEqual(rsrc.uri, attr['ref'])
        self.assertEqual('person', attr['type'])
        # - corporate/organization
        rsrc.is_person = False
        rsrc.is_org = True
        self.assertEqual('org',
                         self.tei_annotater.get_attributes(rsrc)['type'])
        # - geographical/place name
        rsrc.is_org = False
        rsrc.is_place = True
        self.assertEqual('place',
                         self.tei_annotater.get_attributes(rsrc)['type'])

        # EAD
        # assume no viaf/geonames for now (viaf/geonames TODO)
        rsrc.viafid = None
        rsrc.viaf_uri = None
        rsrc.geonames_id = None
        self.assertEqual({'source': 'dbpedia',
                          'authfilenumber': 'TestResource'},
                         self.ead_annotater.get_attributes(rsrc))

    def test_annotate__simplest(self):
        # simplest case: article with a single paragraph and no mixed content or nested tags
        annotations = ilnnames_annotations.article3_result
        nodelist = self.tei.node.xpath('//t:div2[@xml:id="iln42.1183.005"]/t:p', **self.tei_ns)
        article3 = nodelist[0]
        text_content = article3.xpath('normalize-space(.)')
        inserted = self.tei_annotater.annotate(article3, annotations)

        # normalized text should be the same before and after
        self.assertEqual(text_content, article3.xpath('normalize-space(.)'))
        names = article3.xpath('t:name', **self.tei_ns)

        # inspect the tags that were inserted
        self.assertEqual(
            len(annotations['Resources']), len(names),
            'number of resources identified in dbpedia spotlight result' +
            ' should be tagged in the xml')
        self.assertEqual(
            len(annotations['Resources']), inserted,
            'resources identified in spotlight result should match ' +
            'reported inserted count')
        # both resources are places; uri & value should match equivalent dbpedia result
        for i in [0, 1]:
            result = annotations['Resources'][i]
            self.assertEqual('place', names[i].get('type'))
            # uri & value should match dbpedia result
            self.assertEqual(result['URI'], names[i].get('ref'))
            self.assertEqual(result['surfaceForm'], names[i].text)

    def test_annotate__end_tag(self):
        # slightly less simple case
        # - single paragraph article with one nested tag near the end
        annotations = ilnnames_annotations.article1_result
        article = self.tei.node.xpath('//t:div2[@xml:id="iln42.1182.003"]/t:p',
                                      **self.tei_ns)[0]
        text_content = article.xpath('normalize-space(.)')
        hi_rend_text = ''.join(article.xpath('t:hi//text()', **self.tei_ns))
        inserted = self.tei_annotater.annotate(article, annotations)

        # normalized text should be the same before and after
        self.assertEqual(text_content, article.xpath('normalize-space(.)'))

        # inspect the tags that were inserted
        names = article.xpath('.//t:name', **self.tei_ns)
        self.assertEqual(
            len(annotations['Resources']), len(names),
            'the number of resources in the dbpedia spotlight result' +
            ' should match the names tagged in the xml')
        self.assertEqual(
            len(annotations['Resources']), inserted,
            'resources identified in spotlight result should match ' +
            'reported inserted count')
        new_hi_rend_text = ''.join(article.xpath('t:hi//text()', **self.tei_ns))
        self.assertEqual(hi_rend_text, new_hi_rend_text)
        # as before, all resources are places; uri & value should match equivalent dbpedia result
        for i in [0, 1]:
            result = annotations['Resources'][i]
            self.assertEqual('place', names[i].get('type'))
            # uri & value should match dbpedia result
            self.assertEqual(result['URI'], names[i].get('ref'))
            self.assertEqual(result['surfaceForm'], names[i].text)

    def test_annotate_xml__mid_tag(self):
        # second article - single paragraph with a nested tag in the middle
        # - nested tag contains recognized entities
        annotations = ilnnames_annotations.article2_result
        article = self.tei.node.xpath('//t:div2[@xml:id="iln42.1182.005"]/t:p', **self.tei_ns)[0]
        text_content = article.xpath('normalize-space(.)')
        hi_rend_text = ''.join(article.xpath('t:hi//text()', **self.tei_ns))
        inserted = self.tei_annotater.annotate(article, annotations)

        # normalized text should be the same before and after
        self.assertEqual(text_content, article.xpath('normalize-space(.)'))
        new_hi_rend_text = ''.join(article.xpath('t:hi//text()', **self.tei_ns))
        self.assertEqual(hi_rend_text, new_hi_rend_text)

        # inspect the tags that were inserted
        names = article.xpath('.//t:name', **self.tei_ns)
        self.assertEqual(
            len(annotations['Resources']), len(names),
            'the number of resources in the dbpedia spotlight result' +
            ' should match the names tagged in the xml')
        self.assertEqual(
            len(annotations['Resources']), inserted,
            'resources identified in spotlight result should match ' +
            'reported inserted count')
        # as before, all resources are places;
        # uri & value should match equivalent dbpedia result
        for i in [0, 1]:
            result = annotations['Resources'][i]
            dbres = spotlight.DBpediaResource(result['URI'],
                                              spotlight_info=result)
            if dbres.is_person:
                self.assertEqual('person', names[i].get('type'))
            elif dbres.is_place:
                self.assertEqual('place', names[i].get('type'))
            # uri & value should match dbpedia result
            self.assertEqual(dbres.uri, names[i].get('ref'))
            self.assertEqual(result['surfaceForm'], names[i].text)

    def test_annotate_xml__empty_mid_tag(self):
        # article with a nested tag with no recognized entities
        #  ( - manufactured example based on article 3)

        annotations = ilnnames_annotations.article3_result
        nodelist = self.tei.node.xpath('//t:div2[@xml:id="iln42.1183.005a"]/t:p',
                                       **self.tei_ns)
        article3 = nodelist[0]
        text_content = article3.xpath('normalize-space(.)')
        inserted = self.tei_annotater.annotate(article3, annotations)

        # normalized text should be the same before and after
        self.assertEqual(text_content, article3.xpath('normalize-space(.)'))
        names = article3.xpath('t:name', **self.tei_ns)

        # inspect the tags that were inserted
        self.assertEqual(
            len(annotations['Resources']), len(names),
            'resources identified in dbpedia spotlight result ' +
            'should be tagged in the xml')
        self.assertEqual(
            len(annotations['Resources']), inserted,
            'resources identified in spotlight result should ' +
            'match reported inserted count')
        # both resources are places; uri & value should match equivalent dbpedia result
        for i in [0, 1]:
            result = annotations['Resources'][i]
            self.assertEqual('place', names[i].get('type'))
            # uri & value should match dbpedia result
            self.assertEqual(result['URI'], names[i].get('ref'))
            self.assertEqual(result['surfaceForm'], names[i].text)

    def test_annotate_xml__start_tag(self):
        # article with a tag at the beginning

        annotations = ilnnames_annotations.article3_result
        nodelist = self.tei.node.xpath('//t:div2[@xml:id="iln42.1183.005b"]/t:p',
                                       **self.tei_ns)
        article3 = nodelist[0]
        text_content = article3.xpath('normalize-space(.)')
        inserted = self.tei_annotater.annotate(article3, annotations)

        # normalized text should be the same before and after
        self.assertEqual(text_content, article3.xpath('normalize-space(.)'))
        names = article3.xpath('t:name', **self.tei_ns)

        # inspect the tags that were inserted
        self.assertEqual(
            len(annotations['Resources']), len(names),
            'resources identified in dbpedia spotlight result ' +
            'should be tagged in the xml')
        self.assertEqual(
            len(annotations['Resources']), inserted,
            'resources identified in spotlight result should match' +
            ' reported inserted count')
        # both resources are places; uri & value should match equivalent dbpedia result
        for i in [0, 1]:
            result = annotations['Resources'][i]
            self.assertEqual('place', names[i].get('type'))
            # uri & value should match dbpedia result
            self.assertEqual(result['URI'], names[i].get('ref'))
            self.assertEqual(result['surfaceForm'], names[i].text)

    def test_annotate_xml__multiple_nested(self):
        # article with multiple entities in a single nested subelement

        annotations = ilnnames_annotations.article3_result
        nodelist = self.tei.node.xpath('//t:div2[@xml:id="iln42.1183.005c"]/t:p',
                                       **self.tei_ns)
        article3 = nodelist[0]
        text_content = article3.xpath('normalize-space(.)')
        inserted = self.tei_annotater.annotate(article3, annotations)

        # normalized text should be the same before and after
        self.assertEqual(text_content, article3.xpath('normalize-space(.)'))
        names = article3.xpath('.//t:name', **self.tei_ns)

        # inspect the tags that were inserted
        self.assertEqual(
            len(annotations['Resources']), len(names),
            'resources identified in dbpedia spotlight result ' +
            'should be tagged in the xml')
        self.assertEqual(
            len(annotations['Resources']), inserted,
            'resources identified in spotlight result should match ' +
            'reported inserted count')
        # both resources are places; uri & value should match equivalent dbpedia result
        for i in [0, 1]:
            result = annotations['Resources'][i]
            self.assertEqual('place', names[i].get('type'))
            # uri & value should match dbpedia result
            self.assertEqual(result['URI'], names[i].get('ref'))
            self.assertEqual(result['surfaceForm'], names[i].text)

    def test_annotate_xml__with_bibl(self):
        # article with full bibliography / header; processing at div2 level instead of paragraph
        annotations = ilnnames_annotations.article4_result
        article = self.tei.node.xpath('//t:div2[@xml:id="iln38.1069.006"]',
                                      **self.tei_ns)[0]
        text_content = article.xpath('normalize-space(.)')
        inserted = self.tei_annotater.annotate(article, annotations)

        names = article.xpath('.//t:name', **self.tei_ns)

        # inspect the tags that were inserted
        expected = len(annotations['Resources'])
        got = len(names)
        self.assertEqual(
            expected, got,
            'resources identified in dbpedia spotlight result should ' +
            'be tagged in the xml (expected %d, got %d)' % (expected, got))
        self.assertEqual(
            len(annotations['Resources']), inserted,
            'resources identified in spotlight result should match ' +
            'reported inserted count')

        # normalized text should be the same before and after
        self.assertEqual(text_content, article.xpath('normalize-space(.)'))

        # both resources are places; uri & value should match equivalent dbpedia result
        for i in [0, 1]:
            result = annotations['Resources'][i]
            self.assertEqual('place', names[i].get('type'))
            # uri & value should match dbpedia result
            self.assertEqual(result['URI'], names[i].get('ref'))
            self.assertEqual(result['surfaceForm'], names[i].text)

    def test_annotate_xml__with_existing_tags(self):
        # article with names already tagged
        annotations = ilnnames_annotations.article4_result
        article = self.tei.node.xpath('//t:div2[@xml:id="iln38.1069.006a"]',
                                      **self.tei_ns)[0]
        existing_names = article.xpath('.//t:name', **self.tei_ns)
        inserted = self.tei_annotater.annotate(article, annotations)

        names = article.xpath('.//t:name', **self.tei_ns)

        # inspect the tags that were inserted
        expected = len(annotations['Resources'])
        got = len(names)
        # number of tagged names should not increase
        self.assertEqual(
            expected, got,
            'resources identified in dbpedia spotlight result should ' +
            'be tagged in the xml (expected %d, got %d)' % (expected, got))
        self.assertEqual(
            len(annotations['Resources']) - len(existing_names),
            inserted,
            'inserted count should match number of identified ' +
            'resources minus count of existing tagged names')

    @patch('namedropper.util.spotlight')
    def test_ead(self, mock_spotlight):
        # set mock dbpedia resource to have no geonames id
        mock_rsrc = mock_spotlight.DBpediaResource.return_value
        mock_rsrc.geonames_id = None
        mock_rsrc.viafid = None
        mock_rsrc.viaf_uri = None
        mock_rsrc.uri = 'http://dbpedia.org/resource/TestResource'
        # simulate all resources as places
        mock_rsrc.is_person = False
        mock_rsrc.is_org = False
        mock_rsrc.is_place = True

        # first paragraph in biographical note
        paragraph = deepcopy(self.ead.archdesc.biography_history.content[0].node)
        annotations = hobsbaum_annotations.bioghist_result
        text_content = paragraph.xpath('normalize-space(.)')
        inserted = self.ead_annotater.annotate(paragraph, annotations)

        # inspect the tags that were inserted
        names = paragraph.xpath('.//e:persname|.//e:corpname|.//e:geogname',
                                **self.ead_ns)
        expected = len(annotations['Resources'])
        self.assertEqual(
            expected, inserted,
            'resources identified in spotlight result should match ' +
            'reported inserted count (expected %d, got %d)'
            % (expected, inserted))
        got = len(names)
        self.assertEqual(
            expected, got,
            'resources identified in dbpedia spotlight result should ' +
            'be tagged in the xml (expected %d, got %d)'
            % (expected, got))

        geognames = paragraph.xpath('.//e:geogname', **self.ead_ns)
        # geogname source should NOT be geonames since no geonames id was available
        self.assertNotEqual('geonames', geognames[0].get('source'))

        # normalized text should be the same before and after
        self.assertEqual(text_content, paragraph.xpath('normalize-space(.)'))

        # tag name should match resource type;
        # text value should match equivalent dbpedia result
        # TODO: viaf id? dbpedia uri
        for i in range(inserted):
            result = annotations['Resources'][i]
            # all mock resources are places; tag generation tested elsewhere
            expected_tag = 'geogname'
            self.assertEqual('{%s}%s' % (EAD_NAMESPACE, expected_tag), names[i].tag)
            # value should match dbpedia result
            self.assertEqual(result['surfaceForm'], names[i].text)
            # TODO: test viaf id lookup ? (at least for persons)
            #self.assertEqual(result['URI'], names[i].get('ref'))

        # set mock dbpedia resource to return a geonames id
        mock_rsrc.geonames_id = '3356234'
        # re-annotate
        paragraph = deepcopy(self.ead.archdesc.biography_history.content[0].node)
        inserted = annotate_xml(paragraph, annotations, mode='ead')
        names = paragraph.xpath('.//e:geogname', **self.ead_ns)
        # source/auth# should be set from dbpedia geoname identifier
        self.assertEqual('geonames', names[0].get('source'))
        self.assertEqual(mock_rsrc.geonames_id, names[0].get('authfilenumber'))
