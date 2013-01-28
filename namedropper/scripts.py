# file namedropper-py/namedropper/scripts.py
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

import argparse
from eulxml.xmlmap import load_xmlobject_from_file
from eulxml.xmlmap.eadmap import EncodedArchivalDescription as EAD, \
     EAD_NAMESPACE
from eulxml.xmlmap.teimap import Tei, TEI_NAMESPACE

from lxml.etree import XMLSyntaxError, parse
from rdflib import Graph, Namespace, URIRef
import re
from namedropper import spotlight, viaf, util


class LowerCaseAction(argparse.Action):
    # convert input argument to lower case before storing
    def __call__(self, parser, namespace, value, option_string=None):
        setattr(namespace, self.dest, value.lower())



class ScriptBase(object):
    '''Base class for namedropper command-line scripts.

    Directions for use:
      - script description, to be displayed via argparse,
        should be set as class doctring
      - extend :meth:`init_parser` for additional
        command-line arguments
      - extend :meth:`run` with main script functionality

    Init method will initialize the argument parser, parse command-line
    arguments, check that file type is either specified or can be
    auto-detected, and execute :meth:`run`.

    Parser is saved as :attr:`parser`, in case other script logic
    needs reference to it.
    '''

    parser = None
    ''':class:`argparse.ArgumentParser` instance to be initialized by
    :meth:`init_parser` at class instantiation.'''

    def init_parser(self):
        '''Initialize an argument parser with common arguments.
        Currently includes filename and input type.

        Extend to add arguments.
        '''
        parser = argparse.ArgumentParser(description=self.__doc__)
        parser.add_argument('filename', metavar='INPUT_FILE', type=str,
            help='name of the file to be processed')
        parser.add_argument('--input', metavar='INPUT_TYPE', type=str,
            help='type of file to be processed (%(choices)s)',
            action=LowerCaseAction,
            choices=['EAD', 'ead', 'tei', 'TEI', 'text'])
        return parser

    def __init__(self):
        self.parser = self.init_parser()
        self.args = self.parser.parse_args()

        # auto-detect input type if not specified
        if not self.args.input:
            self.args.input = util.autodetect_file_type(self.args.filename)
            # exit if we still don't have an input type
            if not self.args.input:
                print >> sys.stderr, \
                    'Could not determine document input type; ' + \
                    'please specify with --input'
                exit(-1)

        self.run()

    def run(self):
        'placeholder method - extend with script logic'
        # implement/initiate script logic here
        pass

    def init_xml_object(self):
        '''Initialize an xmlobject based on user-specified arguments
        for filename and type.  Returns an instance of the
        appropriate :class:`~eulxml.xmlmap.XmlObject`, or displays
        an error message if the document could not be parsed as XML.'''

        if self.args.input == 'ead':
            xmlobj_class = EAD
        elif self.args.input == 'tei':
            xmlobj_class = Tei

        try:
            return load_xmlobject_from_file(self.args.filename, xmlobj_class)
        except Exception as err:
            print 'Error loading %s as XML: %s' % (self.args.filename, err)
            exit(-1)


