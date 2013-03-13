# file namedropper-py/namedropper/util.py
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

from datetime import datetime
from dateutil.tz import tzlocal
import logging
from lxml.etree import XMLSyntaxError, parse, ProcessingInstruction
import re
from namedropper import spotlight

logger = logging.getLogger(__name__)


def autodetect_file_type(filename):
    '''Attempt to auto-detect input file type.  Currently supported
    types are EAD XML, TEI XML, or text.  Any document that cannot be
    loaded as XML is assumed to be text.

    :returns: "tei", "ead", "text", or None if file type is not recognized
    '''
    # attempt to auto-detect input file type
    try:
        # load as generic xml
        generic_xml = parse(filename)
        root_element = generic_xml.getroot().tag
        # do a simple check on the root element (ignoring namespaces)
        if root_element.endswith('TEI'):
            return 'tei'
        elif root_element.endswith('ead'):
            return 'ead'

    except XMLSyntaxError:
        # Failure to parse as any kind of XML should mean text input.
        # If we need to be more fine-grained, could check error text;
        # should be something similar to this:
        #   Start tag expected, '<' not found, line 1, column 1
        return 'text'
        logger.info('Could not parse %s as XML, assuming text input' %
                    filename)


NORMALIZE_WHITESPACE_RE = re.compile('\s\s+', flags=re.MULTILINE)


def normalize_whitespace(txt, next=None, prev=None):
    '''Normalize whitespace in a string to match the logic
    of ``normalize-space()`` in XPath.  Replaces all internal sequences
    of white space with a single space and conditionally removes
    leading and trailing whitespace.

    :param txt: text string to be normalized
    :param next: optional next string; used to determine
        if trailing whitespace should be removed
    :param prev: optional preceding string; used to determine
        if leading whitepace should be removed
    '''
    txt = NORMALIZE_WHITESPACE_RE.sub(' ', txt)
    if not next or next.startswith(' '):
        txt = txt.rstrip()
    if not prev or prev.endswith(' '):
        txt = txt.lstrip()

    return txt


def enable_oxygen_track_changes(node):
    '''Add a processing instruction to a document with an OxygenXMl
    option to enable the track changes mode.
    '''
    oxy_track_changes = ProcessingInstruction(
        'oxy_options',
        'track_changes="on"'
    )
    # FIXME: shouldn't we be able to add this to the root node
    # and detect if it is already there?
    node.append(oxy_track_changes)


class AnnotateXml(object):

    xml_format = None
    # init should set params about annotation
    # - enable viaf
    # - enable geonames
    # - track changes
    # - tei/ead? (autodetect?)
    #  -- generalize autodetect file to take a node (base/common method?)
    #     and then use that

    current_node = None

    track_changes = False
    track_changes_author = 'namedropper'

    def __init__(self, mode, track_changes=False):
        self.xml_format = mode
        # pass in xmlobj to autodetect type?
        # TODO: list of supported modes
        # TODO: options for viaf/geonames (default to false)
        self.track_changes = track_changes

    def get_tag(self, res):
        '''Get the name of the tag to be inserted, based on the current
        document mode and the type of DBpedia resource.

        :param res: :class:`namedropper.spotlight.DBpediaResource`
           instance for the tag to be inserted

        :returns: string tag
        '''
        if self.xml_format == 'tei':
            tag = self.get_tei_tag(res)
        if self.xml_format == 'ead':
            tag = self.get_ead_tag(res)

        # create the new node in the same namespace as its ancestor node
        if self.current_node is not None and self.current_node.nsmap and \
                self.current_node.prefix in self.current_node.nsmap:
            tag = '{%s}%s' % \
                (self.current_node.nsmap[self.current_node.prefix], tag)
        return tag

    def get_attributes(self, res):
        '''Get the attributes to be inserted, based on the current
        document mode and the type of DBpediaResource.

        :param res: :class:`namedropper.spotlight.DBpediaResource`
        :returns: dictionary of attribute names -> values
        '''
        if self.xml_format == 'tei':
            return self.get_tei_attributes(res)
        if self.xml_format == 'ead':
            return self.get_ead_attributes(res)

    def get_tei_tag(self, res):
        # TEI tags will all use name
        return 'name'

    def get_tei_attributes(self, res):
        tei_type = None
        if res.is_person:
            tei_type = 'person'
        elif res.is_org:
            tei_type = 'org'
        elif res.is_place:
            tei_type = 'place'
        # FIXME: error if type not set
        # TODO: optionally use viaf uri or geonames uri
        return {'type': tei_type, 'ref': res.uri}

    def get_ead_tag(self, res):
        if res.is_person:
            tag = 'persname'
        elif res.is_org:
            tag = 'corpname'
        elif res.is_place:
            tag = 'geogname'
        else:
            # use generic fallback tag for ead if we can't identify the resource type
            tag = 'name'

        return tag

    def get_ead_attributes(self, res):
        attributes = {}
        # TODO: viaf/geonames uri/id needs to be optional
        if res.is_person:
            viafid = None
            if res.viafid:
                viafid = res.viafid
            elif res.viaf_uri:
                viafid = res.viaf_uri.rstrip('/').rsplit('/', 1)[-1]
            else:
                logger.info('VIAF id not found for %s' % res.label)

            if viafid:
                attributes = {
                    'source': 'viaf',
                    'authfilenumber': viafid
                }

        elif res.is_place:
            if res.geonames_id is not None:
                attributes = {'source': 'geonames',
                              'authfilenumber': res.geonames_id}
            else:
                logger.info('GeoNames.org id not found for %s' %
                            res.label)

        # for now, use dbpedia identifiers where no author id is available
        # TODO: *or* if viaf/geonames not requested
        if not attributes:
            # use unique identifier portion of dbpedia uri as id
            base_uri, dbpedia_id = res.uri.rsplit('/', 1)
            attributes = {
                'source': 'dbpedia',
                'authfilenumber': dbpedia_id
            }

        return attributes

    def annotate(self, node, annotations):
        self.current_node = node
        # NOTE: should probably set current_node back to None on completion

        # find all text nodes under this node
        text_list = node.xpath('.//text()')

        # get the list of identified resources from the dbpedia spotlight result
        resources = list(annotations['Resources'])

        # starting values
        current_offset = 0  # current index into the node
        inserted = 0  # number of items inserted into the xml
        item = None  # current dbpedia item being processed

        # aggregate of all normalized text before the current node
        # (used for whitespace normalization on the current node)
        # NOTE: aggregating all previous text in order to properly handle cases where there
        # are multiple whitespace-only nodes in a row
        prev_text = ''

        # iterate until we run out of text nodes or resources
        while (item or resources) and text_list:
            # if there is no current item, get the next item
            if item is None:
                item = resources.pop(0)
                item_offset = int(item['offset'])
                item_end_offset = item_offset + len(item['surfaceForm'])
                # dbpedia resource for this spotlight result
                dbres = spotlight.DBpediaResource(item['URI'],
                                                  spotlight_info=item)

            # current text node to be updated
            text_node = text_list.pop(0)
            next_text = text_list[0] if text_list else ''
            normalized_text = normalize_whitespace(unicode(text_node), next_text, prev_text)
            text_end_offset = current_offset + len(normalized_text)
            # get the parent node for the current text
            parent_node = text_node.getparent()
            # find node immediately after the current text node,
            # so we know where to insert name tags
            if text_node == parent_node.text:
                children = list(parent_node)
                next_node = children[0] if children else None
            elif text_node == parent_node.tail:
                next_node = parent_node.getnext()   # next sibling or None

            # next resource is inside the current text
            if item_offset >= current_offset and item_end_offset <= text_end_offset:
                # text before the item: beginning of this node up to relative item offset
                text_before = normalized_text[:item_offset - current_offset]
                # text after the item: end item offset to end of text, relative to current offset
                text_after = normalized_text[item_end_offset - current_offset:]

                # special case: exact match on start and end offsets *and* the tag
                # matches the tag we would insert (i.e., detected name is already tagged)
                if item_offset == current_offset and item_end_offset == text_end_offset \
                        and parent_node.tag[len(parent_node.prefix or ''):] == self.get_tag(dbres):
                    # store the node so that attributes can be updated if not already set
                    name_node = parent_node
                    existing_tag = True

                else:
                    existing_tag = False
                    # update current text node with the text before the item
                    if text_node == text_node.getparent().text:
                        text_node.getparent().text = text_before
                    elif text_node == text_node.getparent().tail:
                        text_node.getparent().tail = text_before
                        # override the parent node: name tag should be inserted in the
                        # true parent node, not the preceding node
                        parent_node = parent_node.getparent()

                    item_tag = node.makeelement(self.get_tag(dbres),
                                                nsmap=node.nsmap)
                    # text content of the node is the recognized form of the name
                    item_tag.text = item['surfaceForm']

                    # if there is a node immediately after current text, insert new node before it
                    if next_node is not None:
                        node_index = parent_node.index(next_node)
                        parent_node.insert(node_index, item_tag)
                    # otherwise, just append at the end of the parent node
                    else:
                        parent_node.append(item_tag)
                    inserted += 1  # update item tag count

                    if self.track_changes:
                        last_node = self.track_changes_inserted(
                            item_tag, item['surfaceForm'], dbres)
                    else:
                        last_node = item_tag

                    name_node = item_tag   # FIXME: clean up naming conventions

                    # set text after the item to the "tail" text of the new item tag
                    last_node.tail = text_after

                    # set the remainder text as the next text node to be processed
                    # - find via xpath so we have a "smart string" / lxml element string with getparent()
                    remainder_node = last_node.xpath('./following-sibling::text()[1]')[0]

                    text_list.insert(0, remainder_node)

                # set attributes on the newly inserted OR existing name tag
                added_attr = {}
                attributes = self.get_attributes(dbres)
                for attr, val in attributes.iteritems():
                    current_val = name_node.get(attr, None)

                    # add attribute values if they are not already set
                    if current_val is None:
                        name_node.set(attr, val)
                        added_attr[attr] = val

                    # Warn and do NOT set if attributes are present (and different)
                    # FIXME: this may need some modification for EAD (since auth/source are a pair)
                    elif current_val != val:
                        logger.warn('Not setting %s to %s because it already has a value of %s' %
                                    (attr, val, current_val))

                # TODO: track changes on existing tag
                if self.track_changes and existing_tag:
                    last_node = self.track_changes_comment(
                        name_node, attributes, added_attr)

                    # next text node to process is the former name node tail text
                    # replace it with the tail text shifted to the processing instruction
                    text_list.pop(0)
                    # duplicated from insertion logic...
                    remainder_node = last_node.xpath('./following-sibling::text()[1]')[0]
                    text_list.insert(0, remainder_node)
                    #text_list.insert(0, oxy_comment_end.tail)

                # new current offset is the end of the last item
                current_offset = item_end_offset

                # clear item to indicate next one should be grabbed
                item = None

                # add current processed text to previous
                prev_text += text_before + item_tag.text

            # the next item is not inside the current text node
            # update offsets and previous text for the next loop,
            # still looking for the current item
            else:
                current_offset += len(normalized_text)
                # append the processed text to previous
                prev_text += normalized_text

        return inserted

    def track_changes_timestamp(self):
        # generate timestamp to be used for Oxygen track changes
        # format Oxygen requires to be recognized: 20130227T165821-0500
        return datetime.now(tzlocal()).strftime('%Y%m%dT%H%M%S%z')

    def track_changes_inserted(self, new_node, old_text, dbres):
        # create & insert oxygen processing instructions
        # relative to the new node that was just inserted
        timestamp = self.track_changes_timestamp()

        # create a delete marker for the old text
        oxy_delete = ProcessingInstruction(
            'oxy_delete',
            'author="%s" timestamp="%s" content="%s"'
            % (self.track_changes_author, timestamp, old_text))
        # FIXME: escape content in surface form (quotes, etc)

        # Create a marker for the beginning of an insertion.
        # Use the description if possible, to provide enough
        # context for reviewers to determine if this is the correct
        # entity (other information doesn't seem to be useful
        # or is already in the document in another form)
        comment = dbres.description or dbres.label or \
            '(label/description unavailable)'
        # convert quotes to single quotes to avoid breaking comment text
        comment = comment.replace('"', '\'')
        oxy_insert_start = ProcessingInstruction(
            'oxy_insert_start',
            'author="%s" timestamp="%s"' %
            (self.track_changes_author, timestamp) +
            ' comment="%s"' % comment)
        # marker for the end of the insertion
        oxy_insert_end = ProcessingInstruction('oxy_insert_end')

        # - add deletion, then insertion start just before new tag
        parent_node = new_node.getparent()
        parent_node.insert(parent_node.index(new_node), oxy_delete)
        parent_node.insert(parent_node.index(new_node), oxy_insert_start)
        # - insert end *after* new tag
        parent_node.insert(parent_node.index(new_node) + 1,
                           oxy_insert_end)

        # return last processing instruction, since it may
        # need to have 'tail' text appended
        return oxy_insert_end

    def track_changes_comment(self, node, attributes, added_attr):
        comment = ''
        timestamp = self.track_changes_timestamp()

        if added_attr:
            comment += 'Added attribute%s to existing %s tag: ' \
                % ('s' if len(added_attr) != 1 else '',
                   node.xpath('local-name()')) + \
                ', '.join('%s=%s' % (k, v) for k, v in added_attr.iteritems())

        if len(added_attr) != len(attributes):
            comment += '\nDid not replace attribute%s: ' % \
                ('s' if len(attributes) - len(added_attr) != 1 else '') + \
                ', '.join('%s=%s with %s' % (k, node.get(k), v)
                for k, v in attributes.iteritems() if k not in added_attr)
        oxy_comment_start = ProcessingInstruction(
            'oxy_comment_start',
            'author="%s" timestamp="%s"' %
            (self.track_changes_author, timestamp) +
            ' comment="%s"' % comment)
        oxy_comment_end = ProcessingInstruction('oxy_comment_end')
        parent_node = node.getparent()
        parent_node.insert(parent_node.index(node),
                           oxy_comment_start)
        parent_node.insert(parent_node.index(node) + 1,
                           oxy_comment_end)
        # shift any tail text from name node to last pi
        oxy_comment_end.tail = node.tail
        node.tail = ''

        # end comment processing instruction is now last node
        # return in case any tail text needs adjustment
        return oxy_comment_end

    # separate method to generate tag, attributes
    # separate method to add track changes


# TODO: remove this once docstring has been re-used for new class-based
# implementation

def OLDannotate_xml(node, result, mode='tei', track_changes=False):
    '''Annotate xml based on dbpedia spotlight annotation results.  Assumes
    that dbpedia annotate was called on the **normalized** text from this node.
    Currently updates the node that is passed in; whitespace will be normalized in text
    nodes where name tags are inserted.  For TEI, DBpedia URIs are inserted as
    **ref** attributes; since EAD does not support referencing URIs, VIAF ids
    will be used where possible (currently only supports lookup for personal names).

    If recognized names are already tagged as names in the existing XML, no
    new name tag will be inserted; attributes will only be added if they are not
    present in the original node.

    Currently using :mod:`logging` (info and warn) when VIAF look-up fails or
    attributes are not inserted to avoid overwriting existing values.

    When track changes is requested, processing instructions will be added
    around annotated names for review in OxygenXML 14.2+.  In cases where
    a name was untagged, the text will be marked as a deletion and the
    tagged version of the name will be marked as an insertion with a comment
    containing the description of the DBpedia resource, to aid in identifying
    whether the correct resource has been added.  If a recognized name was
    previously tagged, a comment will be added indicating what attributes
    were added, or would have been added if they did not conflict with
    attributes already present in the document.  When using the
    track changes option, it is recommended to also run meth:`enable_oxygen_track_changes`
    once on the document, so that Oxygen will automatically open
    the document with track changes turned on.

    :param node: lxml element node to be updated
    :param result: dbpedia spotlight result, as returned by
        :meth:`namedropper.spotlight.SpotlightClient.annotate`
    :param track_changes: mark changes using OxygenXML track changes
         processing instructions, to enable review in OxygenXML author mode

    :returns: total count of the number of entities inserted into the xml
    '''
    # TEI tags will all use name
    if mode == 'tei':
        name_tag = 'name'
        # create the new node in the same namespace as its parent
        if node.nsmap and node.prefix in node.nsmap:
            name_tag = '{%s}%s' % (node.nsmap[node.prefix], name_tag)

    # find all text nodes under this node
    text_list = node.xpath('.//text()')

    # get the list of identified resources from the dbpedia spotlight result
    resources = list(result['Resources'])

    # starting values
    current_offset = 0  # current index into the node
    inserted = 0  # number of items inserted into the xml
    item = None  # current dbpedia item being processed

    # aggregate of all normalized text before the current node
    # (used for whitespace normalization on the current node)
    # NOTE: aggregating all previous text in order to properly handle cases where there
    # are multiple whitespace-only nodes in a row
    prev_text = ''

    if track_changes:
        # generate timestamp to be used for Oxygen track changes
        # format Oxygen requires to be recognized: 20130227T165821-0500
        now = datetime.now(tzlocal())
        timestamp = now.strftime('%Y%m%dT%H%M%S%z')

    # iterate until we run out of text nodes or resources
    while (item or resources) and text_list:
        # if there is no current item, get the next item
        if item is None:
            item = resources.pop(0)
            item_offset = int(item['offset'])
            item_end_offset = item_offset + len(item['surfaceForm'])
            # dbpedia resource for this spotlight result
            dbres = spotlight.DBpediaResource(item['URI'])

            # determine the tag name to be used for this item
            # TODO/NOTE: might be worth refactoring tag name/attribute logic into
            # a separate function
            tei_type = None
            if dbres.is_person:
                tei_type = 'person'
                ead_tag = 'persname'
            elif dbres.is_org:
                tei_type = 'org'
                ead_tag = 'corpname'
            elif dbres.is_place:
                tei_type = 'place'
                ead_tag = 'geogname'
            else:
                # use generic fallback tag for ead if we can't identify the resource type
                ead_tag = 'name'

            if mode == 'ead':
                name_tag = ead_tag
                # create the new node in the same namespace as its parent
                if node.nsmap and node.prefix in node.nsmap:
                    name_tag = '{%s}%s' % (node.nsmap[node.prefix], name_tag)

        # current text node to be updated
        text_node = text_list.pop(0)
        next_text = text_list[0] if text_list else ''
        normalized_text = normalize_whitespace(unicode(text_node), next_text, prev_text)
        text_end_offset = current_offset + len(normalized_text)
        # get the parent node for the current text
        parent_node = text_node.getparent()
        # find node immediately after the current text node, so we know where to insert name tags
        if text_node == parent_node.text:
            children = list(parent_node)
            next_node = children[0] if children else None
        elif text_node == parent_node.tail:
            next_node = parent_node.getnext()   # next sibling or None

        # next resource is inside the current text
        if item_offset >= current_offset and item_end_offset <= text_end_offset:
            # text before the item: beginning of this node up to relative item offset
            text_before = normalized_text[:item_offset - current_offset]
            # text after the item: end item offset to end of text, relative to current offset
            text_after = normalized_text[item_end_offset - current_offset:]

            # special case: exact match on start and end offsets *and* the tag
            # matches the tag we would insert (i.e., detected name is already tagged)
            if item_offset == current_offset and item_end_offset == text_end_offset \
                    and parent_node.tag[len(parent_node.prefix or ''):] == name_tag:
                # store the node so that attributes can be updated if not already set
                name_node = parent_node
                existing_tag = True

            else:
                existing_tag = False
                # update current text node with the text before the item
                if text_node == text_node.getparent().text:
                    text_node.getparent().text = text_before
                elif text_node == text_node.getparent().tail:
                    text_node.getparent().tail = text_before
                    # override the parent node: name tag should be inserted in the
                    # true parent node, not the preceding node
                    parent_node = parent_node.getparent()

                item_tag = node.makeelement(name_tag, nsmap=node.nsmap)
                # text content of the node is the recognized form of the name
                item_tag.text = item['surfaceForm']

                # if there is a node immediately after current text, insert new node before it
                if next_node is not None:
                    node_index = parent_node.index(next_node)
                    parent_node.insert(node_index, item_tag)
                # otherwise, just append at the end of the parent node
                else:
                    parent_node.append(item_tag)
                inserted += 1  # update item tag count

                last_node = item_tag

                if track_changes:
                    # create & insert oxygen processing instructions
                    # relative to the new node that was just inserted

                    # create a delete marker for the old text
                    oxy_delete = ProcessingInstruction(
                        'oxy_delete',
                        'author="namedropper" timestamp="%s" content="%s"'
                        % (timestamp, item['surfaceForm']))
                    # FIXME: escape content in surface form (quotes, etc)

                    # create a marker for the beginning of an insertion
                    # use the description if possible, to provide enough
                    # context for reviewers to determine if this is the correct
                    # entity (other information doesn't seem to be useful
                    # or is already in the document in another form)
                    comment = dbres.description or dbres.label or \
                        '(label/description unavailable)'
                    oxy_insert_start = ProcessingInstruction(
                        'oxy_insert_start',
                        'author="namedropper" timestamp="%s"' % timestamp +
                        ' comment="%s"' % comment)
                    # marker for the end of the insertion
                    oxy_insert_end = ProcessingInstruction('oxy_insert_end')

                    # - add deletion, then insertion start just before new tag
                    parent_node.insert(parent_node.index(item_tag), oxy_delete)
                    parent_node.insert(parent_node.index(item_tag), oxy_insert_start)
                    # - insert end *after* new tag
                    parent_node.insert(parent_node.index(item_tag) + 1,
                                       oxy_insert_end)

                    # last pi is the one that will get the 'tail' text
                    last_node = oxy_insert_end

                name_node = item_tag

                # set text after the item to the "tail" text of the new item tag
                last_node.tail = text_after

                # set the remainder text as the next text node to be processed
                # - find via xpath so we have a "smart string" / lxml element string with getparent()
                remainder_node = last_node.xpath('./following-sibling::text()[1]')[0]

                text_list.insert(0, remainder_node)

            # add attributes to the name node (inserted or existing), but don't overwrite
            if mode == 'tei':
                attributes = {'ref': item['URI']}
                if tei_type:
                    attributes['type'] = tei_type
            elif mode == 'ead':
                name_tag = ead_tag

                # EAD can't reference dbpedia URI; lookup in VIAF
                attributes = {}
                if ead_tag == 'persname':
                    # TODO: viaf/geonames uri/id needs to be optional
                    viafid = None
                    if dbres.viafid:
                        viafid = dbres.viafid
                    elif dbres.viaf_uri:
                        viafid = dbres.viaf_uri.rstrip('/').rsplit('/', 1)[-1]
                    else:
                        logger.info('VIAF id not found for %s' % item['surfaceForm'])

                    if viafid:
                        attributes = {
                            'source': 'viaf',
                            'authfilenumber': viafid
                        }
                if ead_tag == 'geogname':
                    if dbres.geonames_id is not None:
                        attributes = {'source': 'geonames',
                                      'authfilenumber': dbres.geonames_id}
                    else:
                        logger.info('GeoNames.org id not found for %s' %
                                    item['surfaceForm'])

                # for now, use dbpedia identifiers where no author id is available
                # TODO: *or* if viaf/geonames not requested
                if not attributes:
                    # use unique identifier portion of dbpedia uri as id
                    base_uri, dbpedia_id = item['URI'].rsplit('/', 1)
                    attributes = {
                        'source': 'dbpedia',
                        'authfilenumber': dbpedia_id
                    }

            # set attributes on the newly inserted OR existing name tag
            added_attr = {}
            for attr, val in attributes.iteritems():
                current_val = name_node.get(attr, None)

                # add attribute values if they are not already set
                if current_val is None:
                    name_node.set(attr, val)
                    added_attr[attr] = val

                # Warn and do NOT set if attributes are present (and different)
                # FIXME: this may need some modification for EAD (since auth/source are a pair)
                elif current_val != val:
                    logger.warn('Not setting %s to %s because it already has a value of %s' %
                                (attr, val, current_val))

            # if updating an existing node and track changes is requested
            # add a comment about the change
            if track_changes and existing_tag:
                # FIXME: comment 'author' should probably be a variable
                # TODO: comment text
                comment = ''
                if added_attr:
                    comment += 'Added attribute%s to existing %s tag: ' \
                        % ('s' if len(added_attr) != 1 else '',
                           name_node.xpath('local-name()')) + \
                        ', '.join('%s=%s' % (k, v) for k, v in added_attr.iteritems())

                if len(added_attr) != len(attributes):
                    comment += '\nDid not replace attribute%s: ' % \
                        ('s' if len(attributes) - len(added_attr) != 1 else '') + \
                        ', '.join('%s=%s with %s' % (k, name_node.get(k), v)
                        for k, v in attributes.iteritems() if k not in added_attr)
                oxy_comment_start = ProcessingInstruction(
                    'oxy_comment_start',
                    'author="namedropper" timestamp="%s"' % timestamp +
                    ' comment="%s"' % comment)
                oxy_comment_end = ProcessingInstruction('oxy_comment_end')
                name_parent = name_node.getparent()
                name_parent.insert(name_parent.index(name_node),
                                   oxy_comment_start)
                name_parent.insert(name_parent.index(name_node) + 1,
                                   oxy_comment_end)
                # shift any tail text from name node to last pi
                oxy_comment_end.tail = name_node.tail
                name_node.tail = ''
                # next text node to process is the former name node tail text
                # replace it with the tail text shifted to the processing instruction
                text_list.pop(0)

                # duplicated from insertion logic...
                last_node = oxy_comment_end
                remainder_node = last_node.xpath('./following-sibling::text()[1]')[0]
                text_list.insert(0, remainder_node)
                #text_list.insert(0, oxy_comment_end.tail)

            # new current offset is the end of the last item
            current_offset = item_end_offset

            # clear item to indicate next one should be grabbed
            item = None

            # add current processed text to previous
            prev_text += text_before + item_tag.text

        # the next item is not inside the current text node
        # update offsets and previous text for the next loop,
        # still looking for the current item
        else:
            current_offset += len(normalized_text)
            # append the processed text to previous
            prev_text += normalized_text

    return inserted
