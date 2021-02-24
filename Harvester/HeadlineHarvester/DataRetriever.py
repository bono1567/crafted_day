"""FT Times headlines aggregator. """

import requests
import pandas as pd
from LoggerApi.Logger import Logger

LOGGER = Logger(__file__)


class FinancialTimes:
    """FT Times Headline API aggregator."""
    __url = "http://api.ft.com/content/search/v1"
    __qstr = {"apiKey": "59cbaf20e3e06d3565778e7b14cce0b217a844419dcc5bb1cc3ad4e9"}
    __payload = '{"queryString": "{}","resultContext" : {"aspects" :[ "summary","lifecycle"{}]}}'
    __headers = {
        'X-Api-Key': "59cbaf20e3e06d3565778e7b14cce0b217a844419dcc5bb1cc3ad4e9",
        'Content-Type': "application/json",
        'cache-control': "no-cache",
        'Postman-Token': "53412e50-8805-4b32-a114-bc4f79da2522"
    }

    def __init__(self, query, title=False):
        self.__title = title
        if title:
            self.__payload = '{"queryString": "' + query + \
                             '","resultContext" : {"aspects" :[ "summary","lifecycle","title"]}}'
        else:
            self.__payload = '{"queryString": "' + query + \
                             '","resultContext" : {"aspects" :[ "summary","lifecycle"]}}'
        LOGGER.add('INFO', "Final FT news data for keyword: {}".format(query))

    def response_json(self):
        """Get the JSON response from the URL"""
        return requests.request("POST", self.__url, data=self.__payload, headers=self.__headers,
                                params=self.__qstr).json()

    def get_result(self):
        """Return the result in JSON"""
        return self.response_json()['results'][0]['results']

    def get_final_components(self):
        """:return list of dict with different keys from the API response."""
        results = self.get_result()
        final_result = []
        for result in results:
            try:
                components_dict = {'aspectSet': result['aspectSet'], 'apiUrl': result['apiUrl'],
                                   'publishDate': result['lifecycle']['lastPublishDateTime'][:10],
                                   'summary': result['summary']['excerpt']}
                if self.__title:
                    components_dict['title'] = result['title']['title']
                final_result.append(components_dict)
            except KeyError as exp:
                LOGGER.add('ERROR', "Key Missing in result. {}".format(exp))
        LOGGER.add('INFO', "Final FT get_final_components.")
        return final_result


class FTArrangement(FinancialTimes):
    """Mainly for converting the JSON response to pandas DataFrame."""

    def __init__(self, comp_name="stocks"):
        super().__init__(comp_name, True)
        self.__data = self.get_final_components()

    def get_summary_date_api(self, title=False):
        """:return pandas df with summary, title and other components"""
        LOGGER.add('INFO', "SUMMARY/DATE/API called."
                           " With title as {}.".format(title))
        data = pd.DataFrame(data=self.__data,
                            columns=['aspectSet', 'apiUrl', 'publishDate', 'summary', 'title'])
        if title is False:
            return data.drop(['aspectSet', 'title'], axis=1)
        return data.drop('aspectSet', axis=1)

    def get_summary_for_w2v(self, title=False):
        """:returns List with summary and title which are comma seperated."""
        all_summary = []
        all_title = []
        LOGGER.add('INFO', "SUMMARY/DATE/API/W2V called. With title as {}.".format(title))
        for data_point in self.__data:
            sentence = data_point['summary']
            all_summary.append(sentence)
            if title is True:
                sentence = data_point['title']
                all_title.append(sentence)
        if title is False:
            del all_title
            return all_summary
        return [all_summary, all_title]

# if __name__ == "__main__":
#         A = FTArrangement('John')
#         data = A.get_summary_date_api(True)
#
#         C = FTArrangement('Morgan')
#         C.get_summary_date_api()
