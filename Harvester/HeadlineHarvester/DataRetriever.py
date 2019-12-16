import requests
import pandas as pd


class FinancialTimes:
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

    def responseJSON(self):
        return requests.request("POST", self.__url, data=self.__payload, headers=self.__headers,
                                params=self.__qstr).json()

    def getResult(self):
        return self.responseJSON()['results'][0]['results']

    def getFinalComponents(self):
        results = self.getResult()
        final_result = []
        for result in results:
            components_dict = {'aspectSet': result['aspectSet'], 'apiUrl': result['apiUrl'],
                               'publishDate': result['lifecycle']['lastPublishDateTime'][:10],
                               'summary': result['summary']['excerpt']}
            if self.__title:
                components_dict['title'] = result['title']['title']
            final_result.append(components_dict)

        return final_result


class FTArrangement:

    def __init__(self, comp_name="stocks"):
        self.__Financial_Times = FinancialTimes(comp_name, True)
        self.__data = self.__Financial_Times.getFinalComponents()

    def getSummaryDateAPI(self, title=False):
        data = pd.DataFrame(data=self.__data, columns=['aspectSet', 'apiUrl', 'publishDate', 'summary', 'title'])
        if title is False:
            return data.drop(['aspectSet', 'title'], axis=1)
        return data.drop('aspectSet', axis=1)

    def getSummaryForW2V(self, title=False):
        all_summary = []
        all_title = []
        for data_point in self.__data:
            sentence = data_point['summary'].split()
            all_summary.append(sentence)
            if title is True:
                sentence = data_point['title'].split()
                all_title.append(sentence)
        if title is False:
            del all_title
            return all_summary
        return [all_summary, all_title]




"""if __name__ == "__main__":
    A = FTArrangement('Bombay Stock Exchange')
    B = A.getSummaryDateAPI()
    print(B.head())

    C = A.getSummaryForW2V(False)
    for c in C:
        print(C)"""
