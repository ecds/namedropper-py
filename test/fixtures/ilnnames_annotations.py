# file namedropper-py/test/fixtures/ilnames_annotations.py
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


# saved DBpedia annotation results for fixture document ILNnamesTestSample.xml

article1_result = {
    u'confidence': u'0.2',
    u'sparql': u'',
    u'text': u'Advices from Philadelphia state that the fibre of the plant hibiscos moscheutos is occupying the attention of the merchants at that port as a substitute for linen rags and jute. This plant is indigenous to the Northern States, and grows in abundance in the swampy lands of Pennsylvania, New Jersey, New York, &c. At a moderate calculation, and taking into account the probability of loss from unforeseen causes, three tons and a half of disentegrated fibre can be derived from one acre of ground. Two prominent paper manufacturers of New York have estimated the fibre to be worth 100 dollars per ton, to be used as a substitute for linen rags in the manufacture of paper.-- Liverpool Journal of Commerce.',
    u'support': u'2000',
    u'Resources': [
        {   u'similarityScore': u'0.1041124239563942',
            u'surfaceForm': u'Philadelphia',
            u'support': u'13518',
            u'offset': u'13',
            u'URI': u'http://dbpedia.org/resource/Philadelphia',
            u'percentageOfSecondRank': u'0.6204918900339659',
            u'types': u'DBpedia:City,DBpedia:Settlement,DBpedia:PopulatedPlace,DBpedia:Place,Schema:Place,Schema:City,Freebase:/aviation/airport_operator,Freebase:/aviation,Freebase:/award/award_presenting_organization,Freebase:/award,Freebase:/government/governmental_jurisdiction,Freebase:/government,Freebase:/location/administrative_division,Freebase:/location,Freebase:/location/location,Freebase:/location/citytown,Freebase:/fictional_universe/fictional_setting,Freebase:/fictional_universe,Freebase:/travel/travel_destination,Freebase:/travel,Freebase:/location/statistical_region,Freebase:/olympics/olympic_bidding_city,Freebase:/olympics,Freebase:/business/employer,Freebase:/business,Freebase:/sports/sports_team_location,Freebase:/sports,Freebase:/organization/organization_scope,Freebase:/organization,Freebase:/location/hud_county_place,Freebase:/book/book_subject,Freebase:/book,Freebase:/business/business_location,Freebase:/film/film_location,Freebase:/film,Freebase:/people/place_of_interment,Freebase:/people,Freebase:/location/place_with_neighborhoods,Freebase:/periodicals/newspaper_circulation_area,Freebase:/periodicals,Freebase:/location/hud_foreclosure_area,Freebase:/location/dated_location'},
        {   u'similarityScore': u'0.12121856212615967',
            u'surfaceForm': u'Pennsylvania',
            u'support': u'23220',
            u'offset': u'273',
            u'URI': u'http://dbpedia.org/resource/Pennsylvania',
            u'percentageOfSecondRank': u'0.7424077179145503',
            u'types': u'DBpedia:AdministrativeRegion,DBpedia:PopulatedPlace,DBpedia:Place,Schema:Place,Freebase:/government/political_district,Freebase:/government,Freebase:/book/book_subject,Freebase:/book,Freebase:/government/government,Freebase:/organization/organization_scope,Freebase:/organization,Freebase:/military/military_unit_place_of_origin,Freebase:/military,Freebase:/fictional_universe/fictional_setting,Freebase:/fictional_universe,Freebase:/location/location,Freebase:/location,Freebase:/business/employer,Freebase:/business,Freebase:/location/statistical_region,Freebase:/location/us_state,Freebase:/location/administrative_division,Freebase:/location/dated_location,Freebase:/film/film_location,Freebase:/film,Freebase:/government/governmental_jurisdiction,Freebase:/distilled_spirits/spirit_producing_region,Freebase:/distilled_spirits,Freebase:/organization/organization,Freebase:/education/educational_institution_campus,Freebase:/education,DBpedia:TopicalConcept'},
        {   u'similarityScore': u'0.10080274194478989',
            u'surfaceForm': u'New Jersey',
            u'support': u'16126',
            u'offset': u'287',
            u'URI': u'http://dbpedia.org/resource/New_Jersey',
            u'percentageOfSecondRank': u'0.2113255353203718',
            u'types': u'DBpedia:AdministrativeRegion,DBpedia:PopulatedPlace,DBpedia:Place,Schema:Place,Freebase:/fictional_universe/fictional_setting,Freebase:/fictional_universe,Freebase:/book/book_subject,Freebase:/book,Freebase:/government/political_district,Freebase:/government,Freebase:/military/military_unit_place_of_origin,Freebase:/military,Freebase:/organization/organization_scope,Freebase:/organization,Freebase:/law/court_jurisdiction_area,Freebase:/law,Freebase:/location/location,Freebase:/location,Freebase:/government/governmental_jurisdiction,Freebase:/location/statistical_region,Freebase:/meteorology/cyclone_affected_area,Freebase:/meteorology,Freebase:/location/us_state,Freebase:/film/film_location,Freebase:/film,Freebase:/location/dated_location,Freebase:/location/administrative_division,DBpedia:TopicalConcept'},
        {   u'similarityScore': u'0.08673778921365738',
            u'surfaceForm': u'New York',
            u'support': u'44629',
            u'offset': u'299',
            u'URI': u'http://dbpedia.org/resource/New_York',
            u'percentageOfSecondRank': u'0.9583249046169953',
            u'types': u'DBpedia:AdministrativeRegion,DBpedia:PopulatedPlace,DBpedia:Place,Schema:Place,Freebase:/sports/sports_team_location,Freebase:/sports,Freebase:/wine/wine_region,Freebase:/wine,Freebase:/government/political_district,Freebase:/government,Freebase:/meteorology/cyclone_affected_area,Freebase:/meteorology,Freebase:/government/governmental_jurisdiction,Freebase:/military/military_unit_place_of_origin,Freebase:/military,Freebase:/government/government,Freebase:/business/employer,Freebase:/business,Freebase:/location/administrative_division,Freebase:/location,Freebase:/location/location,Freebase:/location/dated_location,Freebase:/location/us_state,Freebase:/travel/travel_destination,Freebase:/travel,Freebase:/business/asset_owner,Freebase:/fictional_universe/fictional_setting,Freebase:/fictional_universe,Freebase:/film/film_location,Freebase:/film,Freebase:/location/statistical_region,Freebase:/location/citytown,Freebase:/organization/organization_scope,Freebase:/organization,Freebase:/book/book_subject,Freebase:/book,DBpedia:TopicalConcept'},
        {   u'similarityScore': u'0.08673778921365738',
            u'surfaceForm': u'New York',
            u'support': u'44629',
            u'offset': u'534',
            u'URI': u'http://dbpedia.org/resource/New_York',
            u'percentageOfSecondRank': u'0.9583249046169953',
            u'types': u'DBpedia:AdministrativeRegion,DBpedia:PopulatedPlace,DBpedia:Place,Schema:Place,Freebase:/sports/sports_team_location,Freebase:/sports,Freebase:/wine/wine_region,Freebase:/wine,Freebase:/government/political_district,Freebase:/government,Freebase:/meteorology/cyclone_affected_area,Freebase:/meteorology,Freebase:/government/governmental_jurisdiction,Freebase:/military/military_unit_place_of_origin,Freebase:/military,Freebase:/government/government,Freebase:/business/employer,Freebase:/business,Freebase:/location/administrative_division,Freebase:/location,Freebase:/location/location,Freebase:/location/dated_location,Freebase:/location/us_state,Freebase:/travel/travel_destination,Freebase:/travel,Freebase:/business/asset_owner,Freebase:/fictional_universe/fictional_setting,Freebase:/fictional_universe,Freebase:/film/film_location,Freebase:/film,Freebase:/location/statistical_region,Freebase:/location/citytown,Freebase:/organization/organization_scope,Freebase:/organization,Freebase:/book/book_subject,Freebase:/book,DBpedia:TopicalConcept'},
        {   u'similarityScore': u'0.10896724462509155',
            u'surfaceForm': u'Liverpool',
            u'support': u'7899',
            u'offset': u'674',
            u'URI': u'http://dbpedia.org/resource/Liverpool',
            u'percentageOfSecondRank': u'0.45502879386839384',
            u'types': u'DBpedia:City,DBpedia:Settlement,DBpedia:PopulatedPlace,DBpedia:Place,Schema:Place,Schema:City,Freebase:/business/business_location,Freebase:/business,Freebase:/location/dated_location,Freebase:/location,Freebase:/exhibitions/exhibition_subject,Freebase:/exhibitions,Freebase:/location/uk_metropolitan_borough,Freebase:/film/film_location,Freebase:/film,Freebase:/location/uk_statistical_location,Freebase:/location/citytown,Freebase:/government/governmental_jurisdiction,Freebase:/government,Freebase:/business/employer,Freebase:/book/book_subject,Freebase:/book,Freebase:/location/location,Freebase:/location/statistical_region,Freebase:/rail/railway_terminus,Freebase:/rail,Freebase:/sports/sports_team_location,Freebase:/sports,Freebase:/protected_sites/listed_site,Freebase:/protected_sites,Freebase:/fictional_universe/fictional_setting,Freebase:/fictional_universe,Freebase:/location/administrative_division'}
    ],
    u'policy': u'whitelist',
    u'types': u'Person,Place,Organisation'
}

article2_result = {
    u'confidence': u'0.2',
    u'sparql': u'',
    u'text': u"We have before us another work which is also peculiarly suited to the moment. It is written by Mr. D. W. Mitchell, an Englishman who has been a resident in Richmond, Virginia, and is entitled Ten Years in the United States. Being an Englishman's View of Men and Things in the North and South (Smith and Elder). The author states his object to be to explain, if possible, the most active and powerful causes of the great revolution which has taken place in the country in which he lived, working for his livelihood, and, at the same time, observing human nature as developed in Americans and American politics. The residence of Mr. Mitchell in the States commenced in 1848, that year of European convulsions; and he states with confidence that he has better opportunity than common of observing and understanding the people of whom he has written, their habits and feelings, their private and public life, and believes himself capable of pointing out the causes of the split between North and South, not the less because he, with some few others, had marked their rise and progress, and reflected upon the tendency of the life, political and social, of the United States. The author declares that, in considering and explaining the facts which he has here collected, he had to abandon many preconceived ideas and theories of his own, formed before he went to the States; and he admits that it is more than probable that some of the statements he has put forth will conflict with the prejudices and principles of many of his readers; but he protests that he has written carefully and conscientiously, with a desire to arrive at the truth as to the right and wrong of the momentous struggle now going on, sinking for the time sectarian and party prepossessions. The conclusion to which he arrives is that the separation of the North and South are not only natural but desirable; that it therefore inevitably follows, as a matter of course, he does not hesitate to add, that true liberty and real progress will suffer no drawback from such a change. There will probably be those who, in learning these premonitory confessions of a writer on this vexed question, who has been almost a citizen of the Southern capital too, will at once conclude that he is a writer in the Confederate interest purely. Well, perhaps he is so, but to a great extent unconsciously, if not unavoidably; and if his work is taken up with just so much qualification as is implied in these two circumstances of avowal of opinion on the broad question and local tendencies, we think, on the whole, that it will be found to have dealt with the case as nearly fairly and impartially as possible. Apart from the political disquisitions which the volume contains, there is a good deal of characteristic local colouring. The plan of the book is founded on the notion of endeavouring, as far as possible, to let the people of the United States describe themselves, and to let the parties and factions state their own views; and we are informed that many remarks and reflections which are not printed as quotations may be taken to be the deliberate opinions of enlightened Americans, expressed in conversations and discussions at times when hackneyed professions of party were for the hour forgotten. It should be observed that the work contains sketches of life and manners, social and political, at Richmond, at Washington, and at New York mainly, and some chapters are devoted to somewhat remote--for America--history, from which deductions are drawn and brought to bear on modern and immediate circumstances. Even if it had no other merit, the earlier chapters, which do something for raising the close veil which now envelopes the South, its inhabitants, and their ways, would make this book acceptable; but we venture to think that, as a whole, it is a contribution of some value to the knowledge of the United States of America, which most of us are glad to come across at this particular juncture.",
    u'support': u'2000',
    u'Resources': [
        {   u'similarityScore': u'0.12327499687671661',
            u'surfaceForm': u'Richmond, Virginia',
            u'support': u'4297',
            u'offset': u'156',
            u'URI': u'http://dbpedia.org/resource/Richmond,_Virginia',
            u'percentageOfSecondRank': u'-1.0',
            u'types': u'DBpedia:City,DBpedia:Settlement,DBpedia:PopulatedPlace,DBpedia:Place,Schema:Place,Schema:City,Freebase:/location/dated_location,Freebase:/location,Freebase:/location/hud_county_place,Freebase:/location/place_with_neighborhoods,Freebase:/location/administrative_division,Freebase:/location/statistical_region,Freebase:/location/location,Freebase:/location/hud_foreclosure_area,Freebase:/location/citytown,Freebase:/sports/sports_team_location,Freebase:/sports,Freebase:/location/us_county'},
        {   u'similarityScore': u'0.09544765949249268',
            u'surfaceForm': u'United States',
            u'support': u'312771',
            u'offset': u'209',
            u'URI': u'http://dbpedia.org/resource/United_States',
            u'percentageOfSecondRank': u'-1.0',
            u'types': u'DBpedia:Country,DBpedia:PopulatedPlace,DBpedia:Place,Schema:Place,Schema:Country,Freebase:/fictional_universe/fictional_setting,Freebase:/fictional_universe,Freebase:/fictional_universe/ethnicity_in_fiction,Freebase:/exhibitions/exhibition_subject,Freebase:/exhibitions,Freebase:/radio/radio_subject,Freebase:/radio,Freebase:/location/statistical_region,Freebase:/location,Freebase:/food/beer_country_region,Freebase:/food,Freebase:/organization/organization_member,Freebase:/organization,Freebase:/media_common/quotation_subject,Freebase:/media_common,Freebase:/people/place_of_interment,Freebase:/people,Freebase:/business/employer,Freebase:/business,Freebase:/government/political_district,Freebase:/government,Freebase:/film/film_subject,Freebase:/film,Freebase:/film/film_location,Freebase:/location/administrative_division,Freebase:/sports/sport_country,Freebase:/sports,Freebase:/government/governmental_jurisdiction,Freebase:/meteorology/cyclone_affected_area,Freebase:/meteorology,Freebase:/business/asset_owner,Freebase:/military/military_combatant,Freebase:/military,Freebase:/media_common/media_genre,Freebase:/book/book_subject,Freebase:/book,Freebase:/organization/organization_scope,Freebase:/location/location,Freebase:/cvg/computer_game_region,Freebase:/cvg,Freebase:/film/cinematographer,Freebase:/law/patent_office,Freebase:/law,Freebase:/sports/sports_team_location,Freebase:/olympics/olympic_participating_country,Freebase:/olympics,Freebase:/language/human_language,Freebase:/language,Freebase:/location/region,Freebase:/event/speech_topic,Freebase:/event,Freebase:/location/country,Freebase:/law/court_jurisdiction_area,Freebase:/people/profession,Freebase:/law/litigant,Freebase:/location/dated_location,Freebase:/biology/breed_origin,Freebase:/biology,DBpedia:TopicalConcept'},
        {   u'similarityScore': u'0.09544765949249268',
            u'surfaceForm': u'United States',
            u'support': u'312771',
            u'offset': u'1156',
            u'URI': u'http://dbpedia.org/resource/United_States',
            u'percentageOfSecondRank': u'-1.0',
            u'types': u'DBpedia:Country,DBpedia:PopulatedPlace,DBpedia:Place,Schema:Place,Schema:Country,Freebase:/fictional_universe/fictional_setting,Freebase:/fictional_universe,Freebase:/fictional_universe/ethnicity_in_fiction,Freebase:/exhibitions/exhibition_subject,Freebase:/exhibitions,Freebase:/radio/radio_subject,Freebase:/radio,Freebase:/location/statistical_region,Freebase:/location,Freebase:/food/beer_country_region,Freebase:/food,Freebase:/organization/organization_member,Freebase:/organization,Freebase:/media_common/quotation_subject,Freebase:/media_common,Freebase:/people/place_of_interment,Freebase:/people,Freebase:/business/employer,Freebase:/business,Freebase:/government/political_district,Freebase:/government,Freebase:/film/film_subject,Freebase:/film,Freebase:/film/film_location,Freebase:/location/administrative_division,Freebase:/sports/sport_country,Freebase:/sports,Freebase:/government/governmental_jurisdiction,Freebase:/meteorology/cyclone_affected_area,Freebase:/meteorology,Freebase:/business/asset_owner,Freebase:/military/military_combatant,Freebase:/military,Freebase:/media_common/media_genre,Freebase:/book/book_subject,Freebase:/book,Freebase:/organization/organization_scope,Freebase:/location/location,Freebase:/cvg/computer_game_region,Freebase:/cvg,Freebase:/film/cinematographer,Freebase:/law/patent_office,Freebase:/law,Freebase:/sports/sports_team_location,Freebase:/olympics/olympic_participating_country,Freebase:/olympics,Freebase:/language/human_language,Freebase:/language,Freebase:/location/region,Freebase:/event/speech_topic,Freebase:/event,Freebase:/location/country,Freebase:/law/court_jurisdiction_area,Freebase:/people/profession,Freebase:/law/litigant,Freebase:/location/dated_location,Freebase:/biology/breed_origin,Freebase:/biology,DBpedia:TopicalConcept'},
        {   u'similarityScore': u'0.12327499687671661',
            u'surfaceForm': u'Richmond',
            u'support': u'4297',
            u'offset': u'3362',
            u'URI': u'http://dbpedia.org/resource/Richmond,_Virginia',
            u'percentageOfSecondRank': u'-1.0',
            u'types': u'DBpedia:City,DBpedia:Settlement,DBpedia:PopulatedPlace,DBpedia:Place,Schema:Place,Schema:City,Freebase:/location/dated_location,Freebase:/location,Freebase:/location/hud_county_place,Freebase:/location/place_with_neighborhoods,Freebase:/location/administrative_division,Freebase:/location/statistical_region,Freebase:/location/location,Freebase:/location/hud_foreclosure_area,Freebase:/location/citytown,Freebase:/sports/sports_team_location,Freebase:/sports,Freebase:/location/us_county'},
        {   u'similarityScore': u'0.10554943233728409',
            u'surfaceForm': u'Washington',
            u'support': u'4340',
            u'offset': u'3375',
            u'URI': u'http://dbpedia.org/resource/George_Washington',
            u'percentageOfSecondRank': u'-1.0',
            u'types': u'DBpedia:OfficeHolder,DBpedia:Person,Schema:Person,Freebase:/military/military_person,Freebase:/military,Freebase:/government/us_president,Freebase:/government,Freebase:/book/author,Freebase:/book,Freebase:/fictional_universe/person_in_fiction,Freebase:/fictional_universe,Freebase:/event/public_speaker,Freebase:/event,Freebase:/medicine/notable_person_with_medical_condition,Freebase:/medicine,Freebase:/law/constitutional_convention_delegate,Freebase:/law,Freebase:/visual_art/art_subject,Freebase:/visual_art,Freebase:/government/u_s_congressperson,Freebase:/government/politician,Freebase:/people/appointer,Freebase:/people,Freebase:/people/person,Freebase:/government/political_appointer,Freebase:/media_common/dedicatee,Freebase:/media_common,Freebase:/chess/chess_player,Freebase:/chess,Freebase:/organization/organization_member,Freebase:/organization,Freebase:/book/book_subject,Freebase:/people/deceased_person,Freebase:/military/military_commander,DBpedia:TopicalConcept'},
        {   u'similarityScore': u'0.09544765949249268',
            u'surfaceForm': u'America',
            u'support': u'312771',
            u'offset': u'3465',
            u'URI': u'http://dbpedia.org/resource/United_States',
            u'percentageOfSecondRank': u'-1.0',
            u'types': u'DBpedia:Country,DBpedia:PopulatedPlace,DBpedia:Place,Schema:Place,Schema:Country,Freebase:/fictional_universe/fictional_setting,Freebase:/fictional_universe,Freebase:/fictional_universe/ethnicity_in_fiction,Freebase:/exhibitions/exhibition_subject,Freebase:/exhibitions,Freebase:/radio/radio_subject,Freebase:/radio,Freebase:/location/statistical_region,Freebase:/location,Freebase:/food/beer_country_region,Freebase:/food,Freebase:/organization/organization_member,Freebase:/organization,Freebase:/media_common/quotation_subject,Freebase:/media_common,Freebase:/people/place_of_interment,Freebase:/people,Freebase:/business/employer,Freebase:/business,Freebase:/government/political_district,Freebase:/government,Freebase:/film/film_subject,Freebase:/film,Freebase:/film/film_location,Freebase:/location/administrative_division,Freebase:/sports/sport_country,Freebase:/sports,Freebase:/government/governmental_jurisdiction,Freebase:/meteorology/cyclone_affected_area,Freebase:/meteorology,Freebase:/business/asset_owner,Freebase:/military/military_combatant,Freebase:/military,Freebase:/media_common/media_genre,Freebase:/book/book_subject,Freebase:/book,Freebase:/organization/organization_scope,Freebase:/location/location,Freebase:/cvg/computer_game_region,Freebase:/cvg,Freebase:/film/cinematographer,Freebase:/law/patent_office,Freebase:/law,Freebase:/sports/sports_team_location,Freebase:/olympics/olympic_participating_country,Freebase:/olympics,Freebase:/language/human_language,Freebase:/language,Freebase:/location/region,Freebase:/event/speech_topic,Freebase:/event,Freebase:/location/country,Freebase:/law/court_jurisdiction_area,Freebase:/people/profession,Freebase:/law/litigant,Freebase:/location/dated_location,Freebase:/biology/breed_origin,Freebase:/biology,DBpedia:TopicalConcept'},
        {   u'similarityScore': u'0.07225140184164047',
            u'surfaceForm': u'close',
            u'support': u'2203',
            u'offset': u'3662',
            u'URI': u'http://dbpedia.org/resource/Norwich',
            u'percentageOfSecondRank': u'-1.0',
            u'types': u'DBpedia:Settlement,DBpedia:PopulatedPlace,DBpedia:Place,Schema:Place,Freebase:/location/uk_statistical_location,Freebase:/location,Freebase:/location/statistical_region,Freebase:/business/business_location,Freebase:/business,Freebase:/location/location,Freebase:/location/administrative_division,Freebase:/location/dated_location,Freebase:/location/citytown,Freebase:/business/employer,Freebase:/location/uk_non_metropolitan_district,DBpedia:TopicalConcept'},
        {   u'similarityScore': u'0.09544765949249268',
            u'surfaceForm': u'United States of America',
            u'support': u'312771',
            u'offset': u'3871',
            u'URI': u'http://dbpedia.org/resource/United_States',
            u'percentageOfSecondRank': u'-1.0',
            u'types': u'DBpedia:Country,DBpedia:PopulatedPlace,DBpedia:Place,Schema:Place,Schema:Country,Freebase:/fictional_universe/fictional_setting,Freebase:/fictional_universe,Freebase:/fictional_universe/ethnicity_in_fiction,Freebase:/exhibitions/exhibition_subject,Freebase:/exhibitions,Freebase:/radio/radio_subject,Freebase:/radio,Freebase:/location/statistical_region,Freebase:/location,Freebase:/food/beer_country_region,Freebase:/food,Freebase:/organization/organization_member,Freebase:/organization,Freebase:/media_common/quotation_subject,Freebase:/media_common,Freebase:/people/place_of_interment,Freebase:/people,Freebase:/business/employer,Freebase:/business,Freebase:/government/political_district,Freebase:/government,Freebase:/film/film_subject,Freebase:/film,Freebase:/film/film_location,Freebase:/location/administrative_division,Freebase:/sports/sport_country,Freebase:/sports,Freebase:/government/governmental_jurisdiction,Freebase:/meteorology/cyclone_affected_area,Freebase:/meteorology,Freebase:/business/asset_owner,Freebase:/military/military_combatant,Freebase:/military,Freebase:/media_common/media_genre,Freebase:/book/book_subject,Freebase:/book,Freebase:/organization/organization_scope,Freebase:/location/location,Freebase:/cvg/computer_game_region,Freebase:/cvg,Freebase:/film/cinematographer,Freebase:/law/patent_office,Freebase:/law,Freebase:/sports/sports_team_location,Freebase:/olympics/olympic_participating_country,Freebase:/olympics,Freebase:/language/human_language,Freebase:/language,Freebase:/location/region,Freebase:/event/speech_topic,Freebase:/event,Freebase:/location/country,Freebase:/law/court_jurisdiction_area,Freebase:/people/profession,Freebase:/law/litigant,Freebase:/location/dated_location,Freebase:/biology/breed_origin,Freebase:/biology,DBpedia:TopicalConcept'}
    ],
    u'policy': u'whitelist',
    u'types': u'Person,Place,Organisation'}

article3_result = {
    u'confidence': u'0.2',
    u'sparql': u'',
    u'text': u'The annual stocktaking of the Liverpool cotton market shows a total of 392,000 bales, against 622,565 last year. Of the first-mentioned quantity 70,000 are American and 260,050 Surat cotton.',
    u'support': u'2000',
    u'Resources': [
        {   u'similarityScore': u'0.07582904398441315',
            u'surfaceForm': u'Liverpool',
            u'support': u'7899',
            u'offset': u'30',
            u'URI': u'http://dbpedia.org/resource/Liverpool',
            u'percentageOfSecondRank': u'0.656180208265169',
            u'types': u'DBpedia:City,DBpedia:Settlement,DBpedia:PopulatedPlace,DBpedia:Place,Schema:Place,Schema:City,Freebase:/business/business_location,Freebase:/business,Freebase:/location/dated_location,Freebase:/location,Freebase:/exhibitions/exhibition_subject,Freebase:/exhibitions,Freebase:/location/uk_metropolitan_borough,Freebase:/film/film_location,Freebase:/film,Freebase:/location/uk_statistical_location,Freebase:/location/citytown,Freebase:/government/governmental_jurisdiction,Freebase:/government,Freebase:/business/employer,Freebase:/book/book_subject,Freebase:/book,Freebase:/location/location,Freebase:/location/statistical_region,Freebase:/rail/railway_terminus,Freebase:/rail,Freebase:/sports/sports_team_location,Freebase:/sports,Freebase:/protected_sites/listed_site,Freebase:/protected_sites,Freebase:/fictional_universe/fictional_setting,Freebase:/fictional_universe,Freebase:/location/administrative_division'},
        {   u'similarityScore': u'0.05083814263343811',
            u'surfaceForm': u'American',
            u'support': u'3432',
            u'offset': u'156',
            u'URI': u'http://dbpedia.org/resource/Americas',
            u'percentageOfSecondRank': u'0.8267926599427263',
            u'types': u'DBpedia:Continent,DBpedia:PopulatedPlace,DBpedia:Place,Schema:Place,Schema:Continent,Freebase:/location/region,Freebase:/location,Freebase:/location/location,Freebase:/organization/organization_scope,Freebase:/organization,Freebase:/book/book_subject,Freebase:/book,Freebase:/organization/organization,DBpedia:TopicalConcept'}
    ],
    u'policy': u'whitelist',
    u'types': u'Person,Place,Organisation'
}

article4_result = {
    u'confidence': u'0.2',
    u'sparql': u'',
    u'text': u'[Advices had been received] The Illustrated London News vol. 38 no. 1069 p. 27 January 12, 1861 1 paragraphhttp://pid.emory.edu/ark:/25593/18k Advices had been received at Baltimore stating that the Dominican Government had taken forcible possession of the guano islands in the Caribbean Sea belonging to America.',
    u'support': u'2000',
    u'Resources': [
        {   u'similarityScore': u'0.0751926600933075',
            u'surfaceForm': u'ark',
            u'support': u'5961',
            u'offset': u'128',
            u'URI': u'http://dbpedia.org/resource/Arkansas',
            u'percentageOfSecondRank': u'0.6585130498956222',
            u'types': u'DBpedia:AdministrativeRegion,DBpedia:PopulatedPlace,DBpedia:Place,Schema:Place,Freebase:/fictional_universe/fictional_setting,Freebase:/fictional_universe,Freebase:/government/governmental_jurisdiction,Freebase:/government,Freebase:/location/statistical_region,Freebase:/location,Freebase:/government/political_district,Freebase:/location/us_state,Freebase:/meteorology/cyclone_affected_area,Freebase:/meteorology,Freebase:/people/place_of_interment,Freebase:/people,Freebase:/book/book_subject,Freebase:/book,Freebase:/military/military_unit_place_of_origin,Freebase:/military,Freebase:/location/dated_location,Freebase:/location/administrative_division,Freebase:/location/location,Freebase:/organization/organization_scope,Freebase:/organization,DBpedia:TopicalConcept'},
        {   u'similarityScore': u'0.08204954117536545',
            u'surfaceForm': u'Baltimore',
            u'support': u'4113',
            u'offset': u'172',
            u'URI': u'http://dbpedia.org/resource/Baltimore',
            u'percentageOfSecondRank': u'0.9154368448299174',
            u'types': u'DBpedia:City,DBpedia:Settlement,DBpedia:PopulatedPlace,DBpedia:Place,Schema:Place,Schema:City,Freebase:/business/employer,Freebase:/business,Freebase:/location/statistical_region,Freebase:/location,Freebase:/visual_art/art_owner,Freebase:/visual_art,Freebase:/people/place_of_interment,Freebase:/people,Freebase:/fictional_universe/fictional_setting,Freebase:/fictional_universe,Freebase:/location/administrative_division,Freebase:/sports/sports_team_location,Freebase:/sports,Freebase:/location/place_with_neighborhoods,Freebase:/government/governmental_jurisdiction,Freebase:/government,Freebase:/location/dated_location,Freebase:/location/citytown,Freebase:/location/hud_foreclosure_area,Freebase:/architecture/architectural_structure_owner,Freebase:/architecture,Freebase:/location/hud_county_place,Freebase:/location/us_county,Freebase:/film/film_location,Freebase:/film,Freebase:/business/business_location,Freebase:/location/location'},
        {   u'similarityScore': u'0.11089084297418594',
            u'surfaceForm': u'Dominican',
            u'support': u'5928',
            u'offset': u'199',
            u'URI': u'http://dbpedia.org/resource/Dominican_Republic',
            u'percentageOfSecondRank': u'0.7708973624983934',
            u'types': u'DBpedia:Country,DBpedia:PopulatedPlace,DBpedia:Place,Schema:Place,Schema:Country,Freebase:/olympics/olympic_participating_country,Freebase:/olympics,Freebase:/organization/organization_scope,Freebase:/organization,Freebase:/business/board_member,Freebase:/business,Freebase:/sports/sports_team_location,Freebase:/sports,Freebase:/sports/sport_country,Freebase:/location/country,Freebase:/location,Freebase:/organization/organization_member,Freebase:/location/location,Freebase:/time/time_zone,Freebase:/time,Freebase:/location/dated_location,Freebase:/location/statistical_region,Freebase:/location/administrative_division,Freebase:/book/book_subject,Freebase:/book,Freebase:/meteorology/cyclone_affected_area,Freebase:/meteorology,Freebase:/government/governmental_jurisdiction,Freebase:/government,DBpedia:TopicalConcept'},
        {   u'similarityScore': u'0.09556137770414352',
            u'surfaceForm': u'America',
            u'support': u'3432',
            u'offset': u'305',
            u'URI': u'http://dbpedia.org/resource/Americas',
            u'percentageOfSecondRank': u'0.7114575038840932',
            u'types': u'DBpedia:Continent,DBpedia:PopulatedPlace,DBpedia:Place,Schema:Place,Schema:Continent,Freebase:/location/region,Freebase:/location,Freebase:/location/location,Freebase:/organization/organization_scope,Freebase:/organization,Freebase:/book/book_subject,Freebase:/book,Freebase:/organization/organization,DBpedia:TopicalConcept'}
    ],
    u'policy': u'whitelist',
    u'types': u'Person,Place,Organisation'
}
