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
from lxml import etree
from mock import patch, Mock
from StringIO import StringIO

from namedropper import spotlight
from namedropper.util import autodetect_file_type, AnnotateXml
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

    def test_is_insertable(self):
        rsrc = Mock(spec=spotlight.DBpediaResource)
        rsrc.uri = 'http://dbpedia.org/resource/TestResource'
        rsrc.is_person = False
        rsrc.is_place = False
        rsrc.is_org = False

        # EAD & tag could not be determined
        self.assertFalse(self.ead_annotater.is_insertable(rsrc, 'test'))

        # TEI and type attribute not set
        self.assertFalse(self.tei_annotater.is_insertable(rsrc, 'test'))

        # known type - should be ok for either
        rsrc.is_org = True
        self.assertTrue(self.ead_annotater.is_insertable(rsrc, 'test'))
        self.assertTrue(self.tei_annotater.is_insertable(rsrc, 'test'))

    def test_annotate__simplest(self):
        # simplest case: article with a single paragraph and no mixed content or nested tags
        annotations = ilnnames_annotations.article3_result
        nodelist = self.tei.node.xpath('//t:div2[@xml:id="iln42.1183.005"]/t:p', **self.tei_ns)
        article3 = deepcopy(nodelist[0])
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

    @patch('namedropper.util.spotlight')
    def test_annotate__viaf_geonames(self, mock_spotlight):
        # setup mock dbpedia resource
        mock_rsrc = mock_spotlight.DBpediaResource.return_value
        mock_rsrc.geonames_id = '67890'
        mock_rsrc.geonames_uri = 'http://sws.geonames.org/67890/'
        mock_rsrc.viafid = '12345'
        mock_rsrc.viaf_uri = 'http://viaf.org/viaf/12345'
        mock_rsrc.uri = 'http://dbpedia.org/resource/TestResource'
        # first simulate all resources as person
        mock_rsrc.is_person = True
        mock_rsrc.is_org = False
        mock_rsrc.is_place = False

        # simple case from first test
        annotations = ilnnames_annotations.article3_result
        nodelist = self.tei.node.xpath('//t:div2[@xml:id="iln42.1183.005"]/t:p', **self.tei_ns)
        article3 = deepcopy(nodelist[0])

        # is person, has viaf, but viaf not enabled
        article3 = deepcopy(nodelist[0])
        self.tei_annotater.annotate(article3, annotations)
        names = article3.xpath('t:name', **self.tei_ns)
        # dbpedia uri should still be used
        self.assertEqual(
            mock_rsrc.uri, names[0].get('ref'),
            'dbpedia uri should be used for persons when viaf lookup is not enabled')
        # enable viaf
        self.tei_annotater.viaf = True
        article3 = deepcopy(nodelist[0])
        self.tei_annotater.annotate(article3, annotations)
        names = article3.xpath('t:name', **self.tei_ns)
        self.assertEqual(
            mock_rsrc.viaf_uri, names[0].get('ref'),
            'viaf uri should be used when available and viaf lookup enabled')
        # no viaf uri
        mock_rsrc.viaf_uri = None
        article3 = deepcopy(nodelist[0])
        self.tei_annotater.annotate(article3, annotations)
        names = article3.xpath('t:name', **self.tei_ns)
        self.assertEqual(
            mock_rsrc.uri, names[0].get('ref'),
            'dbpedia uri should be used if viaf uri is unavailabe')

        # simulate place resource
        mock_rsrc.is_place = True
        mock_rsrc.is_person = False
        # is place, has geonames uri, but geonames not enabled
        article3 = deepcopy(nodelist[0])
        self.tei_annotater.annotate(article3, annotations)
        names = article3.xpath('t:name', **self.tei_ns)
        # dbpedia uri should still be used
        self.assertEqual(mock_rsrc.uri, names[0].get('ref'))
        # enable geonames
        self.tei_annotater.geonames = True
        article3 = deepcopy(nodelist[0])
        self.tei_annotater.annotate(article3, annotations)
        names = article3.xpath('t:name', **self.tei_ns)
        self.assertEqual(mock_rsrc.geonames_uri, names[0].get('ref'))
        mock_rsrc.geonames_uri = None
        article3 = deepcopy(nodelist[0])
        self.tei_annotater.annotate(article3, annotations)
        names = article3.xpath('t:name', **self.tei_ns)
        # dbpedia uri should be used if geonames uri is not available
        self.assertEqual(mock_rsrc.uri, names[0].get('ref'))

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
        inserted = self.ead_annotater.annotate(paragraph, annotations)
        names = paragraph.xpath('.//e:geogname', **self.ead_ns)
        # should *NOT* be set because annotater is not set to use geonames
        self.assertNotEqual(
            'geonames', names[0].get('source'),
            'geonames source should not be used when geonames is not enabled')

        paragraph = deepcopy(self.ead.archdesc.biography_history.content[0].node)
        # enable geonames
        self.ead_annotater.geonames = True
        inserted = self.ead_annotater.annotate(paragraph, annotations)
        names = paragraph.xpath('.//e:geogname', **self.ead_ns)
        # source/auth# should be set from dbpedia geoname identifier
        self.assertEqual('geonames', names[0].get('source'))
        self.assertEqual(mock_rsrc.geonames_id, names[0].get('authfilenumber'))

        # test viaf
        mock_rsrc.viafid = '98765'
        mock_rsrc.is_person = True
        mock_rsrc.is_place = False
        # viaf not enabled
        paragraph = deepcopy(self.ead.archdesc.biography_history.content[0].node)
        inserted = self.ead_annotater.annotate(paragraph, annotations)
        names = paragraph.xpath('.//e:persname', **self.ead_ns)
        self.assertNotEqual(
            'viaf', names[0].get('source'),
            'viaf source should not be used when viaf is not enabled')

        paragraph = deepcopy(self.ead.archdesc.biography_history.content[0].node)
        # enable viaf lookup
        self.ead_annotater.viaf = True
        inserted = self.ead_annotater.annotate(paragraph, annotations)
        names = paragraph.xpath('.//e:persname', **self.ead_ns)
        # source/auth# should be set from dbpedia viaf identifier
        self.assertEqual('viaf', names[0].get('source'))
        self.assertEqual(mock_rsrc.viafid, names[0].get('authfilenumber'))

    def test_track_changes_inserted(self):
        xml = '''<p>some text <name>Some Name</name></p>'''
        test_doc = etree.parse(StringIO(xml))
        name_node = list(test_doc.iter('name'))[0]
        rsrc = Mock(spec=spotlight.DBpediaResource)
        rsrc.uri = 'http://dbpedia.org/resource/TestResource'

        initial_length = len(list(test_doc.iter()))

        # no label/description
        rsrc.description = None
        rsrc.label = None
        old_text = 'Some Name'
        self.tei_annotater.track_changes_inserted(
            name_node, old_text, rsrc)
        # should have added 3 nodes: 1 deletion, 2 for start/end insertion
        self.assertEqual(initial_length + 3, len(list(test_doc.iter())))

        preceding_sibs = list(name_node.itersiblings(preceding=True))
        following_sib = list(name_node.itersiblings())

        # second (farthest away) preceding sibling should be deletion,
        # then insert start
        deletion = preceding_sibs[1]
        insert_start = preceding_sibs[0]
        # insert end should be immediately after the node
        insert_end = following_sib[0]
        # inspect deletion marker
        self.assertEqual('oxy_delete', deletion.target)
        self.assertEqual(self.tei_annotater.track_changes_author,
                         deletion.get('author'))
        self.assertEqual(old_text, deletion.get('content'))

        # inspect insert start
        self.assertEqual('oxy_insert_start', insert_start.target)
        self.assertEqual(self.tei_annotater.track_changes_author,
                         insert_start.get('author'))
        self.assertEqual('(label/description unavailable)',
                         insert_start.get('comment'))
        # inspect insert end
        self.assertEqual('oxy_insert_end', insert_end.target)

        # reset to test dbpedia with label
        test_doc = etree.parse(StringIO(xml))
        name_node = list(test_doc.iter('name'))[0]

        # no description but a label
        rsrc.label = 'Some person\'s name'
        old_text = 'Some Name'
        self.tei_annotater.track_changes_inserted(
            name_node, old_text, rsrc)
        insert_start = list(name_node.itersiblings(preceding=True))[0]
        self.assertEqual(
            rsrc.label, insert_start.get('comment'),
            'dbpedia resource label should be used as insert comment ' +
            ' when no description is available')

        # reset to test dbpedia with description
        test_doc = etree.parse(StringIO(xml))
        name_node = list(test_doc.iter('name'))[0]

        # description (with quotes)
        rsrc.description = 'This person was "born" and is famous for ...'
        escaped_desc = rsrc.description.replace('"', '\'')

        old_text = 'Some Name'
        self.tei_annotater.track_changes_inserted(
            name_node, old_text, rsrc)
        insert_start = list(name_node.itersiblings(preceding=True))[0]
        self.assertEqual(
            escaped_desc, insert_start.get('comment'),
            'dbpedia resource description should be used as ' +
            'insertion comment when available')

    def test_track_changes_comment(self):
        xml = '''<p>some text <name>Some Name</name> more text</p>'''
        test_doc = etree.parse(StringIO(xml))
        name_node = list(test_doc.iter('name'))[0]
        initial_length = len(list(test_doc.iter()))

        attr = {'source': 'dbpedia', 'authfilenumber': '12345'}
        added_attr = attr
        self.tei_annotater.track_changes_comment(
            name_node, attr, added_attr)

        # should have added 2 nodes: start/end of comment
        self.assertEqual(initial_length + 2, len(list(test_doc.iter())))

        comment_start = list(name_node.itersiblings(preceding=True))[0]
        comment_end = list(name_node.itersiblings())[0]

        self.assertEqual('oxy_comment_start', comment_start.target)
        self.assertEqual(self.tei_annotater.track_changes_author,
                         comment_start.get('author'))
        self.assertEqual('oxy_comment_end', comment_end.target)

        # inspect comment contents - all added
        comment_text = comment_start.get('comment')
        self.assert_('Added attributes ' in comment_text)
        for name, value in added_attr.iteritems():
            self.assert_('%s=%s' % (name, value) in comment_text)

        # reset to test not all attributes added
        test_doc = etree.parse(StringIO(xml))
        name_node = list(test_doc.iter('name'))[0]
        name_node.set('authfilenumber', 'foo')
        added_attr = {'source': 'dbpedia'}
        self.tei_annotater.track_changes_comment(
            name_node, attr, added_attr)
        comment_start = list(name_node.itersiblings(preceding=True))[0]
        comment_text = comment_start.get('comment')
        self.assert_('Added attribute ' in comment_text)
        for name, value in added_attr.iteritems():
            self.assert_('%s=%s' % (name, value) in comment_text)
        self.assert_('Did not replace attribute: %s=%s with %s' %
                     ('authfilenumber', 'foo', '12345')
                     in comment_text)

        # reset to test NO attributes added
        test_doc = etree.parse(StringIO(xml))
        name_node = list(test_doc.iter('name'))[0]
        name_node.set('source', 'viaf')
        name_node.set('authfilenumber', '98765')
        added_attr = {}
        self.tei_annotater.track_changes_comment(
            name_node, attr, added_attr)
        comment_start = list(name_node.itersiblings(preceding=True))[0]
        comment_text = comment_start.get('comment')
        self.assert_('Added attribute' not in comment_text)
        for name, value in added_attr.iteritems():
            self.assert_('%s=%s' % (name, value) in comment_text)
        self.assert_('Did not replace attributes: ' in comment_text)
        for name, value in attr.iteritems():
            self.assert_('%s=%s with %s' % (name, name_node.get(name), value)
                         in comment_text)
