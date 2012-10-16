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

from namedropper.util import autodetect_file_type, annotate_xml
from testcore import main

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

    article1_result = {u'confidence': u'0.2',
        u'sparql': u'',
        u'support': u'2000',
        u'text': u'[Advices from Philadelphia] Advices from Philadelphia state that the fibre of the plant hibiscos moscheutos is occupying the attention of the merchants at that port as a substitute for linen rags and jute. This plant is indigenous to the Northern States, and grows in abundance in the swampy lands of Pennsylvania, New Jersey, New York, &c. At a moderate calculation, and taking into account the probability of loss from unforeseen causes, three tons and a half of disentegrated fibre can be derived from one acre of ground. Two prominent paper manufacturers of New York have estimated the fibre to be worth 100 dollars per ton, to be used as a substitute for linen rags in the manufacture of paper.-- Liverpool Journal of Commerce.',
        u'policy': u'whitelist',
        u'types': u'Person,Place,Organisation',
        u'Resources': [
            {u'support': u'13518',
            u'URI': u'http://dbpedia.org/resource/Philadelphia',
            u'surfaceForm': u'Philadelphia',
            u'offset': u'14',
            u'percentageOfSecondRank': u'0.6204918900339659',
            u'similarityScore': u'0.1041124239563942',
            u'types': u'DBpedia:City,DBpedia:Settlement,DBpedia:PopulatedPlace,DBpedia:Place,Schema:Place,Schema:City,Freebase:/aviation/airport_operator,Freebase:/aviation,Freebase:/award/award_presenting_organization,Freebase:/award,Freebase:/government/governmental_jurisdiction,Freebase:/government,Freebase:/location/administrative_division,Freebase:/location,Freebase:/location/location,Freebase:/location/citytown,Freebase:/fictional_universe/fictional_setting,Freebase:/fictional_universe,Freebase:/travel/travel_destination,Freebase:/travel,Freebase:/location/statistical_region,Freebase:/olympics/olympic_bidding_city,Freebase:/olympics,Freebase:/business/employer,Freebase:/business,Freebase:/sports/sports_team_location,Freebase:/sports,Freebase:/organization/organization_scope,Freebase:/organization,Freebase:/location/hud_county_place,Freebase:/book/book_subject,Freebase:/book,Freebase:/business/business_location,Freebase:/film/film_location,Freebase:/film,Freebase:/people/place_of_interment,Freebase:/people,Freebase:/location/place_with_neighborhoods,Freebase:/periodicals/newspaper_circulation_area,Freebase:/periodicals,Freebase:/location/hud_foreclosure_area,Freebase:/location/dated_location'}, {u'support': u'13518',
            u'URI': u'http://dbpedia.org/resource/Philadelphia',
            u'surfaceForm': u'Philadelphia',
            u'offset': u'41',
            u'percentageOfSecondRank': u'0.6204918900339659',
            u'similarityScore': u'0.1041124239563942',
            u'types': u'DBpedia:City,DBpedia:Settlement,DBpedia:PopulatedPlace,DBpedia:Place,Schema:Place,Schema:City,Freebase:/aviation/airport_operator,Freebase:/aviation,Freebase:/award/award_presenting_organization,Freebase:/award,Freebase:/government/governmental_jurisdiction,Freebase:/government,Freebase:/location/administrative_division,Freebase:/location,Freebase:/location/location,Freebase:/location/citytown,Freebase:/fictional_universe/fictional_setting,Freebase:/fictional_universe,Freebase:/travel/travel_destination,Freebase:/travel,Freebase:/location/statistical_region,Freebase:/olympics/olympic_bidding_city,Freebase:/olympics,Freebase:/business/employer,Freebase:/business,Freebase:/sports/sports_team_location,Freebase:/sports,Freebase:/organization/organization_scope,Freebase:/organization,Freebase:/location/hud_county_place,Freebase:/book/book_subject,Freebase:/book,Freebase:/business/business_location,Freebase:/film/film_location,Freebase:/film,Freebase:/people/place_of_interment,Freebase:/people,Freebase:/location/place_with_neighborhoods,Freebase:/periodicals/newspaper_circulation_area,Freebase:/periodicals,Freebase:/location/hud_foreclosure_area,Freebase:/location/dated_location'}, {u'support': u'23220',
            u'URI': u'http://dbpedia.org/resource/Pennsylvania',
            u'surfaceForm': u'Pennsylvania',
            u'offset': u'301',
            u'percentageOfSecondRank': u'0.7424077179145503',
            u'similarityScore': u'0.12121856212615967',
            u'types': u'DBpedia:AdministrativeRegion,DBpedia:PopulatedPlace,DBpedia:Place,Schema:Place,Freebase:/government/political_district,Freebase:/government,Freebase:/book/book_subject,Freebase:/book,Freebase:/government/government,Freebase:/organization/organization_scope,Freebase:/organization,Freebase:/military/military_unit_place_of_origin,Freebase:/military,Freebase:/fictional_universe/fictional_setting,Freebase:/fictional_universe,Freebase:/location/location,Freebase:/location,Freebase:/business/employer,Freebase:/business,Freebase:/location/statistical_region,Freebase:/location/us_state,Freebase:/location/administrative_division,Freebase:/location/dated_location,Freebase:/film/film_location,Freebase:/film,Freebase:/government/governmental_jurisdiction,Freebase:/distilled_spirits/spirit_producing_region,Freebase:/distilled_spirits,Freebase:/organization/organization,Freebase:/education/educational_institution_campus,Freebase:/education,DBpedia:TopicalConcept'},
            {u'support': u'16126',
            u'URI': u'http://dbpedia.org/resource/New_Jersey',
            u'surfaceForm': u'New Jersey',
            u'offset': u'315',
            u'percentageOfSecondRank': u'0.2113255353203718',
            u'similarityScore': u'0.10080274194478989',
            u'types': u'DBpedia:AdministrativeRegion,DBpedia:PopulatedPlace,DBpedia:Place,Schema:Place,Freebase:/fictional_universe/fictional_setting,Freebase:/fictional_universe,Freebase:/book/book_subject,Freebase:/book,Freebase:/government/political_district,Freebase:/government,Freebase:/military/military_unit_place_of_origin,Freebase:/military,Freebase:/organization/organization_scope,Freebase:/organization,Freebase:/law/court_jurisdiction_area,Freebase:/law,Freebase:/location/location,Freebase:/location,Freebase:/government/governmental_jurisdiction,Freebase:/location/statistical_region,Freebase:/meteorology/cyclone_affected_area,Freebase:/meteorology,Freebase:/location/us_state,Freebase:/film/film_location,Freebase:/film,Freebase:/location/dated_location,Freebase:/location/administrative_division,DBpedia:TopicalConcept'},
            {u'support': u'44629',
            u'URI': u'http://dbpedia.org/resource/New_York',
            u'surfaceForm': u'New York',
            u'offset': u'327',
            u'percentageOfSecondRank': u'0.9583249046169953',
            u'similarityScore': u'0.08673778921365738',
            u'types': u'DBpedia:AdministrativeRegion,DBpedia:PopulatedPlace,DBpedia:Place,Schema:Place,Freebase:/sports/sports_team_location,Freebase:/sports,Freebase:/wine/wine_region,Freebase:/wine,Freebase:/government/political_district,Freebase:/government,Freebase:/meteorology/cyclone_affected_area,Freebase:/meteorology,Freebase:/government/governmental_jurisdiction,Freebase:/military/military_unit_place_of_origin,Freebase:/military,Freebase:/government/government,Freebase:/business/employer,Freebase:/business,Freebase:/location/administrative_division,Freebase:/location,Freebase:/location/location,Freebase:/location/dated_location,Freebase:/location/us_state,Freebase:/travel/travel_destination,Freebase:/travel,Freebase:/business/asset_owner,Freebase:/fictional_universe/fictional_setting,Freebase:/fictional_universe,Freebase:/film/film_location,Freebase:/film,Freebase:/location/statistical_region,Freebase:/location/citytown,Freebase:/organization/organization_scope,Freebase:/organization,Freebase:/book/book_subject,Freebase:/book,DBpedia:TopicalConcept'},
            {u'support': u'44629',
            u'URI': u'http://dbpedia.org/resource/New_York',
            u'surfaceForm': u'New York',
            u'offset': u'562',
            u'percentageOfSecondRank': u'0.9583249046169953',
            u'similarityScore': u'0.08673778921365738',
            u'types': u'DBpedia:AdministrativeRegion,DBpedia:PopulatedPlace,DBpedia:Place,Schema:Place,Freebase:/sports/sports_team_location,Freebase:/sports,Freebase:/wine/wine_region,Freebase:/wine,Freebase:/government/political_district,Freebase:/government,Freebase:/meteorology/cyclone_affected_area,Freebase:/meteorology,Freebase:/government/governmental_jurisdiction,Freebase:/military/military_unit_place_of_origin,Freebase:/military,Freebase:/government/government,Freebase:/business/employer,Freebase:/business,Freebase:/location/administrative_division,Freebase:/location,Freebase:/location/location,Freebase:/location/dated_location,Freebase:/location/us_state,Freebase:/travel/travel_destination,Freebase:/travel,Freebase:/business/asset_owner,Freebase:/fictional_universe/fictional_setting,Freebase:/fictional_universe,Freebase:/film/film_location,Freebase:/film,Freebase:/location/statistical_region,Freebase:/location/citytown,Freebase:/organization/organization_scope,Freebase:/organization,Freebase:/book/book_subject,Freebase:/book,DBpedia:TopicalConcept'},
            {u'support': u'7899',
            u'URI': u'http://dbpedia.org/resource/Liverpool',
            u'surfaceForm': u'Liverpool',
            u'offset': u'702',
            u'percentageOfSecondRank': u'0.45502879386839384',
            u'similarityScore': u'0.10896724462509155',
            u'types': u'DBpedia:City,DBpedia:Settlement,DBpedia:PopulatedPlace,DBpedia:Place,Schema:Place,Schema:City,Freebase:/business/business_location,Freebase:/business,Freebase:/location/dated_location,Freebase:/location,Freebase:/exhibitions/exhibition_subject,Freebase:/exhibitions,Freebase:/location/uk_metropolitan_borough,Freebase:/film/film_location,Freebase:/film,Freebase:/location/uk_statistical_location,Freebase:/location/citytown,Freebase:/government/governmental_jurisdiction,Freebase:/government,Freebase:/business/employer,Freebase:/book/book_subject,Freebase:/book,Freebase:/location/location,Freebase:/location/statistical_region,Freebase:/rail/railway_terminus,Freebase:/rail,Freebase:/sports/sports_team_location,Freebase:/sports,Freebase:/protected_sites/listed_site,Freebase:/protected_sites,Freebase:/fictional_universe/fictional_setting,Freebase:/fictional_universe,Freebase:/location/administrative_division'}
        ]}

    article1_result = {u'confidence': u'0.2', u'sparql': u'', u'text': u'Advices from Philadelphia state that the fibre of the plant hibiscos moscheutos is occupying the attention of the merchants at that port as a substitute for linen rags and jute. This plant is indigenous to the Northern States, and grows in abundance in the swampy lands of Pennsylvania, New Jersey, New York, &c. At a moderate calculation, and taking into account the probability of loss from unforeseen causes, three tons and a half of disentegrated fibre can be derived from one acre of ground. Two prominent paper manufacturers of New York have estimated the fibre to be worth 100 dollars per ton, to be used as a substitute for linen rags in the manufacture of paper.-- Liverpool Journal of Commerce.', u'support': u'2000', u'Resources': [{u'similarityScore': u'0.1041124239563942', u'surfaceForm': u'Philadelphia', u'support': u'13518', u'offset': u'13', u'URI': u'http://dbpedia.org/resource/Philadelphia', u'percentageOfSecondRank': u'0.6204918900339659', u'types': u'DBpedia:City,DBpedia:Settlement,DBpedia:PopulatedPlace,DBpedia:Place,Schema:Place,Schema:City,Freebase:/aviation/airport_operator,Freebase:/aviation,Freebase:/award/award_presenting_organization,Freebase:/award,Freebase:/government/governmental_jurisdiction,Freebase:/government,Freebase:/location/administrative_division,Freebase:/location,Freebase:/location/location,Freebase:/location/citytown,Freebase:/fictional_universe/fictional_setting,Freebase:/fictional_universe,Freebase:/travel/travel_destination,Freebase:/travel,Freebase:/location/statistical_region,Freebase:/olympics/olympic_bidding_city,Freebase:/olympics,Freebase:/business/employer,Freebase:/business,Freebase:/sports/sports_team_location,Freebase:/sports,Freebase:/organization/organization_scope,Freebase:/organization,Freebase:/location/hud_county_place,Freebase:/book/book_subject,Freebase:/book,Freebase:/business/business_location,Freebase:/film/film_location,Freebase:/film,Freebase:/people/place_of_interment,Freebase:/people,Freebase:/location/place_with_neighborhoods,Freebase:/periodicals/newspaper_circulation_area,Freebase:/periodicals,Freebase:/location/hud_foreclosure_area,Freebase:/location/dated_location'}, {u'similarityScore': u'0.12121856212615967', u'surfaceForm': u'Pennsylvania', u'support': u'23220', u'offset': u'273', u'URI': u'http://dbpedia.org/resource/Pennsylvania', u'percentageOfSecondRank': u'0.7424077179145503', u'types': u'DBpedia:AdministrativeRegion,DBpedia:PopulatedPlace,DBpedia:Place,Schema:Place,Freebase:/government/political_district,Freebase:/government,Freebase:/book/book_subject,Freebase:/book,Freebase:/government/government,Freebase:/organization/organization_scope,Freebase:/organization,Freebase:/military/military_unit_place_of_origin,Freebase:/military,Freebase:/fictional_universe/fictional_setting,Freebase:/fictional_universe,Freebase:/location/location,Freebase:/location,Freebase:/business/employer,Freebase:/business,Freebase:/location/statistical_region,Freebase:/location/us_state,Freebase:/location/administrative_division,Freebase:/location/dated_location,Freebase:/film/film_location,Freebase:/film,Freebase:/government/governmental_jurisdiction,Freebase:/distilled_spirits/spirit_producing_region,Freebase:/distilled_spirits,Freebase:/organization/organization,Freebase:/education/educational_institution_campus,Freebase:/education,DBpedia:TopicalConcept'}, {u'similarityScore': u'0.10080274194478989', u'surfaceForm': u'New Jersey', u'support': u'16126', u'offset': u'287', u'URI': u'http://dbpedia.org/resource/New_Jersey', u'percentageOfSecondRank': u'0.2113255353203718', u'types': u'DBpedia:AdministrativeRegion,DBpedia:PopulatedPlace,DBpedia:Place,Schema:Place,Freebase:/fictional_universe/fictional_setting,Freebase:/fictional_universe,Freebase:/book/book_subject,Freebase:/book,Freebase:/government/political_district,Freebase:/government,Freebase:/military/military_unit_place_of_origin,Freebase:/military,Freebase:/organization/organization_scope,Freebase:/organization,Freebase:/law/court_jurisdiction_area,Freebase:/law,Freebase:/location/location,Freebase:/location,Freebase:/government/governmental_jurisdiction,Freebase:/location/statistical_region,Freebase:/meteorology/cyclone_affected_area,Freebase:/meteorology,Freebase:/location/us_state,Freebase:/film/film_location,Freebase:/film,Freebase:/location/dated_location,Freebase:/location/administrative_division,DBpedia:TopicalConcept'}, {u'similarityScore': u'0.08673778921365738', u'surfaceForm': u'New York', u'support': u'44629', u'offset': u'299', u'URI': u'http://dbpedia.org/resource/New_York', u'percentageOfSecondRank': u'0.9583249046169953', u'types': u'DBpedia:AdministrativeRegion,DBpedia:PopulatedPlace,DBpedia:Place,Schema:Place,Freebase:/sports/sports_team_location,Freebase:/sports,Freebase:/wine/wine_region,Freebase:/wine,Freebase:/government/political_district,Freebase:/government,Freebase:/meteorology/cyclone_affected_area,Freebase:/meteorology,Freebase:/government/governmental_jurisdiction,Freebase:/military/military_unit_place_of_origin,Freebase:/military,Freebase:/government/government,Freebase:/business/employer,Freebase:/business,Freebase:/location/administrative_division,Freebase:/location,Freebase:/location/location,Freebase:/location/dated_location,Freebase:/location/us_state,Freebase:/travel/travel_destination,Freebase:/travel,Freebase:/business/asset_owner,Freebase:/fictional_universe/fictional_setting,Freebase:/fictional_universe,Freebase:/film/film_location,Freebase:/film,Freebase:/location/statistical_region,Freebase:/location/citytown,Freebase:/organization/organization_scope,Freebase:/organization,Freebase:/book/book_subject,Freebase:/book,DBpedia:TopicalConcept'}, {u'similarityScore': u'0.08673778921365738', u'surfaceForm': u'New York', u'support': u'44629', u'offset': u'534', u'URI': u'http://dbpedia.org/resource/New_York', u'percentageOfSecondRank': u'0.9583249046169953', u'types': u'DBpedia:AdministrativeRegion,DBpedia:PopulatedPlace,DBpedia:Place,Schema:Place,Freebase:/sports/sports_team_location,Freebase:/sports,Freebase:/wine/wine_region,Freebase:/wine,Freebase:/government/political_district,Freebase:/government,Freebase:/meteorology/cyclone_affected_area,Freebase:/meteorology,Freebase:/government/governmental_jurisdiction,Freebase:/military/military_unit_place_of_origin,Freebase:/military,Freebase:/government/government,Freebase:/business/employer,Freebase:/business,Freebase:/location/administrative_division,Freebase:/location,Freebase:/location/location,Freebase:/location/dated_location,Freebase:/location/us_state,Freebase:/travel/travel_destination,Freebase:/travel,Freebase:/business/asset_owner,Freebase:/fictional_universe/fictional_setting,Freebase:/fictional_universe,Freebase:/film/film_location,Freebase:/film,Freebase:/location/statistical_region,Freebase:/location/citytown,Freebase:/organization/organization_scope,Freebase:/organization,Freebase:/book/book_subject,Freebase:/book,DBpedia:TopicalConcept'}, {u'similarityScore': u'0.10896724462509155', u'surfaceForm': u'Liverpool', u'support': u'7899', u'offset': u'674', u'URI': u'http://dbpedia.org/resource/Liverpool', u'percentageOfSecondRank': u'0.45502879386839384', u'types': u'DBpedia:City,DBpedia:Settlement,DBpedia:PopulatedPlace,DBpedia:Place,Schema:Place,Schema:City,Freebase:/business/business_location,Freebase:/business,Freebase:/location/dated_location,Freebase:/location,Freebase:/exhibitions/exhibition_subject,Freebase:/exhibitions,Freebase:/location/uk_metropolitan_borough,Freebase:/film/film_location,Freebase:/film,Freebase:/location/uk_statistical_location,Freebase:/location/citytown,Freebase:/government/governmental_jurisdiction,Freebase:/government,Freebase:/business/employer,Freebase:/book/book_subject,Freebase:/book,Freebase:/location/location,Freebase:/location/statistical_region,Freebase:/rail/railway_terminus,Freebase:/rail,Freebase:/sports/sports_team_location,Freebase:/sports,Freebase:/protected_sites/listed_site,Freebase:/protected_sites,Freebase:/fictional_universe/fictional_setting,Freebase:/fictional_universe,Freebase:/location/administrative_division'}], u'policy': u'whitelist', u'types': u'Person,Place,Organisation'}
    article3_result = {u'confidence': u'0.2', u'sparql': u'', u'text': u'The annual stocktaking of the Liverpool cotton market shows a total of 392,000 bales, against 622,565 last year. Of the first-mentioned quantity 70,000 are American and 260,050 Surat cotton.', u'support': u'2000', u'Resources': [{u'similarityScore': u'0.07582904398441315', u'surfaceForm': u'Liverpool', u'support': u'7899', u'offset': u'30', u'URI': u'http://dbpedia.org/resource/Liverpool', u'percentageOfSecondRank': u'0.656180208265169', u'types': u'DBpedia:City,DBpedia:Settlement,DBpedia:PopulatedPlace,DBpedia:Place,Schema:Place,Schema:City,Freebase:/business/business_location,Freebase:/business,Freebase:/location/dated_location,Freebase:/location,Freebase:/exhibitions/exhibition_subject,Freebase:/exhibitions,Freebase:/location/uk_metropolitan_borough,Freebase:/film/film_location,Freebase:/film,Freebase:/location/uk_statistical_location,Freebase:/location/citytown,Freebase:/government/governmental_jurisdiction,Freebase:/government,Freebase:/business/employer,Freebase:/book/book_subject,Freebase:/book,Freebase:/location/location,Freebase:/location/statistical_region,Freebase:/rail/railway_terminus,Freebase:/rail,Freebase:/sports/sports_team_location,Freebase:/sports,Freebase:/protected_sites/listed_site,Freebase:/protected_sites,Freebase:/fictional_universe/fictional_setting,Freebase:/fictional_universe,Freebase:/location/administrative_division'}, {u'similarityScore': u'0.05083814263343811', u'surfaceForm': u'American', u'support': u'3432', u'offset': u'156', u'URI': u'http://dbpedia.org/resource/Americas', u'percentageOfSecondRank': u'0.8267926599427263', u'types': u'DBpedia:Continent,DBpedia:PopulatedPlace,DBpedia:Place,Schema:Place,Schema:Continent,Freebase:/location/region,Freebase:/location,Freebase:/location/location,Freebase:/organization/organization_scope,Freebase:/organization,Freebase:/book/book_subject,Freebase:/book,Freebase:/organization/organization,DBpedia:TopicalConcept'}], u'policy': u'whitelist', u'types': u'Person,Place,Organisation'}

    def setUp(self):
        self.tei = load_xmlobject_from_file(FIXTURES['tei'], Tei)

    def test_annotate_xml(self):
        tei_ns = {'namespaces': {'t': TEI_NAMESPACE}}
        # simplest case: article 3 is a single paragraph with no mixed content / nested tags
        nodelist = self.tei.node.xpath('//t:div2[3]/t:p', **tei_ns)
        article3 = nodelist[0]
        text_content = article3.xpath('normalize-space(.)')
        annotate_xml(article3, self.article3_result)

        # normalized text should be the same before and after
        self.assertEqual(text_content, article3.xpath('normalize-space(.)'))
        names = article3.xpath('t:name', **tei_ns)

        # inspect the tags that were inserted
        self.assertEqual(len(self.article3_result['Resources']), len(names),
            'resources identified in dbpedia spotlight result should be tagged in the xml')
        # both resources are places; uri & value should match equivalent dbpedia result
        for i in [0, 1]:
            result = self.article3_result['Resources'][i]
            self.assertEqual('place', names[i].get('type'))
            # uri & value should match dbpedia result
            self.assertEqual(result['URI'], names[i].get('res'))
            self.assertEqual(result['surfaceForm'], names[i].text)

        # first article - single paragraph with one nested tag at the very end
        article = self.tei.node.xpath('//t:div2[1]/t:p', **tei_ns)[0]
        text_content = article.xpath('normalize-space(.)')
        hi_rend_text = ''.join(article.xpath('t:hi/text()', **tei_ns))
        annotate_xml(article, self.article1_result)
        # normalized text should be the same before and after
        self.assertEqual(text_content, article.xpath('normalize-space(.)'))

        # inspect the tags that were inserted
        names = article.xpath('.//t:name', **tei_ns)
        self.assertEqual(len(self.article1_result['Resources']), len(names),
            'the number of resources in the dbpedia spotlight result should match the names tagged in the xml')
        new_hi_rend_text = ''.join(article.xpath('t:hi//text()', namespaces={'t': TEI_NAMESPACE}))
        self.assertEqual(hi_rend_text, new_hi_rend_text)
        # as before, all resources are places; uri & value should match equivalent dbpedia result
        for i in [0, 1]:
            result = self.article1_result['Resources'][i]
            self.assertEqual('place', names[i].get('type'))
            # uri & value should match dbpedia result
            self.assertEqual(result['URI'], names[i].get('res'))
            self.assertEqual(result['surfaceForm'], names[i].text)


if __name__ == '__main__':
    main()

