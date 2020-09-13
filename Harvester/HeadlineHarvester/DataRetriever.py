import requests
import pandas as pd
from LoggerApi.Logger import Logger

"""TODO: Multiple logger issue still pertains but the dat is not getting duplicated or APIs are not being called 
twice. """


class FinancialTimes(Logger):
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
        super().__init__(FinancialTimes.__name__)
        self.__title = title
        if title:
            self.__payload = '{"queryString": "' + query + \
                             '","resultContext" : {"aspects" :[ "summary","lifecycle","title"]}}'
        else:
            self.__payload = '{"queryString": "' + query + \
                             '","resultContext" : {"aspects" :[ "summary","lifecycle"]}}'
        self.add('INFO', "Final FT news data for keyword: {}".format(query))

    def response_json(self):

        return requests.request("POST", self.__url, data=self.__payload, headers=self.__headers,
                                params=self.__qstr).json()

    def get_result(self):
        return self.response_json()['results'][0]['results']

    def get_final_components(self):
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
            except KeyError as e:
                self.add('ERROR', "Key Missing in result. {}".format(e))
        self.add('INFO', "Final FT get_final_components.")
        return final_result


class FTArrangement(FinancialTimes):
    def __init__(self, comp_name="stocks"):
        super().__init__(FTArrangement.__name__)
        super().__init__(comp_name, True)
        self.__data = self.get_final_components()

    def get_summary_date_api(self, title=False):
        self.add('INFO', "SUMMARY/DATE/API called. With title as {}.".format(title))
        data = pd.DataFrame(data=self.__data, columns=['aspectSet', 'apiUrl', 'publishDate', 'summary', 'title'])
        if title is False:
            return data.drop(['aspectSet', 'title'], axis=1)
        return data.drop('aspectSet', axis=1)

    def get_summary_for_w2v(self, title=False):
        all_summary = []
        all_title = []
        self.add('INFO', "SUMMARY/DATE/API/W2V called. With title as {}.".format(title))
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
