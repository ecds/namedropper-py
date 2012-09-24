#!/usr/bin/env python

import argparse
from eulxml.xmlmap import load_xmlobject_from_file
from eulxml.xmlmap.eadmap import EncodedArchivalDescription as EAD

import spotlight


# TODO: may want to set up a local mirror of dbpedia spotlight,
# to avoid hitting production server for development work....


class LookupNames(object):
    # object to wrap script functionality

    _queried_text = set()

    def __init__(self):
        # parse command-line arguments and init spotlight client
        parser = argparse.ArgumentParser(description='Look up named entities in a file.')
        parser.add_argument('filename', metavar='INPUT_FILE', type=str,
            help='name of the file to be processed')
        # FIXME: could we reliably auto-detect TEI/EAD/text file?
        parser.add_argument('--input', metavar='INPUT_TYPE', type=str, required=True,
            help='type of file to be processed (%(choices)s)', choices=['EAD', 'ead', 'text'])
        # dbpedia-specific options
        spotlight_opts = parser.add_argument_group('DBpedia Spotlight options')
        spotlight_opts.add_argument('--confidence', '-c', metavar='N', type=float, default=0.4,
            help='minimum confidence score (default: %(default)s)')
        spotlight_opts.add_argument('--support', '-s', metavar='N', type=int, default=20,
            help='minimum support score (default: %(default)s)')
        spotlight_opts.add_argument('--types', '-t', metavar='TYPES', type=str, default='',  # Person,Place,Organisation',
            help='restrict to specific types of resources, e.g. Person,Place,Organization')  # (default: %(default)s)')

        # NOTE! restricting to person/place/org leaves out literary prizes, which are otherwise being
        # recognized; check if these be tagged/identified in EAD for inclusion
        # - probably do want to exclude dates (don't seem to be recognized in a useful way...)
        self.args = parser.parse_args()

        spotlight_args = {'confidence': self.args.confidence, 'support': self.args.support,
            'types': self.args.types}

        # for now, script only has a single mode: output a list of recognized names and URIs

        self.sc = spotlight.SpotlightClient(**spotlight_args)

        if self.args.input.lower() == 'ead':
            try:
                ead = load_xmlobject_from_file(self.args.filename, EAD)
            except Exception as err:
                print 'Error loading %s as EAD: %s' % (self.args.filename, err)
                return -1

            print 'Looking up names in EAD by section'
            for label, text_list in self.get_ead_sections(ead):
                print "\n%s" % label
                for txt in text_list:
                    # skip repeat look-ups
                    # (e.g. "undated correspondence" or "miscellaneous invitations")
                    if txt in self._queried_text:
                        continue
                    # print text so user can compare original and recognized names
                    print txt
                    self.list_names(txt)

        elif self.args.input == 'text':
            # NOTE: would probably need to be read / processed in chunks
            # if we want to handle text files of any significant size
            with open(self.args.filename) as txtfile:
                text = txtfile.read()

            self.list_names(text)

        # Brief summary of API call activity
        print '\nMade %d API call%s in %s' % (self.sc.total_api_calls, 's' if self.sc.total_api_calls != 1 else '',
            self.sc.total_api_duration)

    def list_names(self, text):
        # run spotlight annotation on a text string and print out identified
        # resources
        self._queried_text.add(text)

        results = self.sc.annotate(text)

        if not 'Resources' in results:
            print 'No resources identified'
            return

        # NOTE: dbpedia annotate result is per offset within the text, so
        # may include duplicates - e.g., different "surfaceForm" text variants
        # for the same URI, or same exact text and URI

        # TODO: consider uniquifying & alphabetizing this list
        # (or possibly use candidates instead of annotate for list output...)

        # TODO: in list mode, maybe return a list of tuples (or similar), to
        # allow the results of multiple calls to be aggregated
        for resource in results['Resources']:
            print '%s  %s' % (resource['surfaceForm'].ljust(40), resource['URI'])

    def get_ead_sections(self, ead):
        # generator: returns tuples of section label, list of strings

        # biographical statement
        yield (unicode(ead.archdesc.biography_history.head),
            [unicode(p) for p in ead.archdesc.biography_history.content])
        # note: beware that using unicode on xmlmap elements normalizes whitespace
        # (good for lookup, bad for annotating original xml)

        # return sections for series/subseries
        if ead.dsc.c and ead.dsc.c[0].c:
            for c01 in ead.dsc.c:
                for section in self.get_ead_component_sections(c01):
                    yield section
        # return elements for findingaid with a single container list
        else:
            yield ('Container List',
                [unicode(c.did.unittitle) for c in ead.dsc.c])

    def get_ead_component_sections(self, cseries):
        # recursive generator for c01/c02 series/subseries elements
        series_title = unicode(cseries.did.unittitle)
        if cseries.scope_content:
            yield ('%s : %s' % (series_title, unicode(cseries.scope_content.head)),
                [unicode(p) for p in cseries.scope_content.content])
        if cseries.hasSubseries():
            for subseries in cseries.c:
                for section in self.get_ead_component_sections(subseries):
                    yield section
        else:
            yield ('%s: item descriptions' % series_title,
                [unicode(c.did.unittitle) for c in cseries.c])


if __name__ == '__main__':
    LookupNames()
