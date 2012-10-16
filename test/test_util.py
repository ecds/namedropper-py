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

from namedropper.util import autodetect_file_type
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

if __name__ == '__main__':
    main()

