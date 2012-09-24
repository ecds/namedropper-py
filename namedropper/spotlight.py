## spotlight.py

from datetime import datetime, timedelta
import requests


class SpotlightClient(object):
    '''Client for interacting with DBpedia Spotlight via REST API.

    http://wiki.dbpedia.org/spotlight/usersmanual?v=ssd

    '''

    default_url = 'http://spotlight.dbpedia.org/rest'
    'Default base url for DBpedia Spotlight web service'

    # TODO: keep track of number of queries & response time?
    _api_calls = []

    def __init__(self, base_url=None, confidence=None, support=None, types=None):
        if base_url is None:
            self.base_url = self.default_url
        else:
            self.base_url = base_url

        self.default_confidence = confidence
        self.default_support = support

        # support python list or string input
        if isinstance(types, list):
            types = ','.join(types)
        self.default_types = types

    def annotate(self, text, confidence=None, support=None, types=None):
        # types e.g., 'Person,Place'  or ['Person', 'Place']
        annotate_url = '%s/annotate' % self.base_url
        data = {'text': text}

        if confidence is not None:
            data['confidence'] = confidence
        elif self.default_confidence:
            data['confidence'] = self.default_confidence

        if support is not None:
            data['support'] = support
        elif self.default_support:
            data['support'] = self.default_support

        if types is not None:
            # if types is a list, convert to comma-delimited string
            if isinstance(types, list):
                types = ','.join(types)
            # otherwise, just pass as given
            data['types'] = types
        elif self.default_types:
            data['types'] = self.default_types

        response = self._call(annotate_url, data=data,
            headers={'accept': 'application/json',
                    'content-type': 'application/x-www-form-urlencoded'})

        # response = requests.post(annotate_url, data=data,
        #     headers={'accept': 'application/json',
        #             'content-type': 'application/x-www-form-urlencoded'})
        # # API docs suggest using POST instead of GET for large text content;
        # for POST, a content-type of application/x-www-form-urlencoded is required

        if response.status_code == requests.codes.ok:
            return self._clean_response(response.json)

        # if response was not ok, raise the error
        response.raise_for_status()

    @property
    def total_api_calls(self):
        'number of API calls made'
        return len(self._api_calls)

    @property
    def total_api_duration(self):
        ':class:`datetime.timedelta` - total duration of all API calls'
        return sum(self._api_calls, timedelta())

    def _call(self, url, **kwargs):
        # wrapper around request to allow keeping track of number
        # and duration of api calls
        start = datetime.now()
        response = requests.post(url, **kwargs)
        self._api_calls.append(datetime.now() - start)
        return response

    def _clean_response(self, data):
        '''Recursive function to clean up DBPedia Spotlight JSON result,
        which returns key names beginning with `@`.

        For a dictionary, return a new copy of the same dictionary, where '@' has been removed
        from keyds and value has been cleaned with :meth:`_clean_response`.  For a list, returns
        a list with every value cleaned by :meth:`_clean_response`.  Any other content is
        currently returned unchanged.
        '''
        if isinstance(data, dict):
            return dict((k.replace('@', ''),
                        self._clean_response(v)) for k, v in data.iteritems())
        elif isinstance(data, list):
            return [self._clean_response(i) for i in data]
        else:
            return data

        # NOTE: may not belong here, but somewhere: consider splitting out resource types
        # from comma-delimited string list into a python list
