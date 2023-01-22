"""FT Times headlines aggregator. """

import datetime

import dateutil.relativedelta
import requests
import pandas as pd
from GoogleNews import GoogleNews
from Constants import SEPARATOR, API_MARK, API_FT, MONTHS
from LoggerApi.Logger import Logger


def get_date(date):
    """Convert date to datetime"""
    day = int(date.split()[0])
    month = MONTHS[date.split()[1].lower()]
    current_time = datetime.datetime.now()
    year = int(current_time.year)
    final_date = datetime.date(year, month, day)
    if final_date >= datetime.datetime.now().date():
        final_date = final_date - dateutil.relativedelta.relativedelta(years=1)
    return final_date


class GoogleNewsApi(Logger):
    """Market news from Google"""
    __gn = GoogleNews(lang='en')

    def __init__(self, stock, period=None):
        super().__init__(GoogleNewsApi.__name__)
        if period is not None:
            self.__gn.set_period("{}d".format(period))
        self.__keyword = stock
        self.__gn.get_news(stock)

    def get_result(self):
        """Get refined result with datetime."""
        result = self.__gn.results()
        final_answer = []
        for headline in result:
            val_head = {}
            if headline["datetime"] is not None:
                val_head["publishDate"] = headline["datetime"]
            else:
                val_head["publishDate"] = get_date(headline["date"])
            val_head['title'] = headline['title']
            val_head['apiUrl'] = headline['link']
            val_head['summary'] = headline['title']
            final_answer.append(val_head)
        return final_answer

    def get_final_components(self):
        """:return list of dict with different keys from the API response."""
        results = self.get_result()
        final_result = []
        for result in results:
            try:
                result['summary'] = result['summary'].replace("<em>", "").replace("</em>", "")
                final_result.append(result)
            except KeyError as exp:
                self.add('ERROR', "Key Missing in result. {}".format(exp))
        self.add('INFO', "Final Google Headlines get_final_components. Note: Headlines only, no summary.")
        return final_result


class MarketAux(Logger):
    """Market AUX Data Aggregator"""
    __url = "https://api.marketaux.com/v1/news/all"
    __qstr = {"api_token": API_MARK}

    def __init__(self, parameters, limit=100):
        super().__init__(MarketAux.__name__)
        self.__qstr.update({"limit": str(limit)})
        self.__qstr.update(parameters)

    def response_json(self):
        """Get the API response"""
        return requests.request("GET", self.__url, params=self.__qstr).json()

    def get_result(self):
        """Return the result in the expected format"""
        self.add("INFO", "Data retrieval")
        data = self.response_json()
        data = data["data"]
        final_data = []
        for headline in data:
            entities = self.__get_entities(headline["entities"])
            final_headline = {"title": headline["title"],
                              "publishDate": headline["published_at"],
                              "summary": entities["summary"],
                              "sentiment": entities["sentiment"],
                              "apiUrl": headline["url"]}
            final_data.append(final_headline)
        return final_data

    def get_final_components(self):
        """:return list of dict with different keys from the API response."""
        results = self.get_result()
        final_result = []
        for result in results:
            try:
                result['summary'] = result['summary'].replace("<em>", "").replace("</em>", "")
                final_result.append(result)
            except KeyError as exp:
                self.add('ERROR', "Key Missing in result. {}".format(exp))
        self.add('INFO', "Final Mark AUX get_final_components.")
        return final_result

    def __get_entities(self, entities):
        """:return Summary of highlight entities."""
        result = {}
        highlights = ""
        sentiments = ""
        for ent in entities:
            if ent['symbol'] in self.__qstr['symbols']:
                for highlight in ent['highlights']:
                    highlights += highlight["highlight"]
                    highlights += SEPARATOR
            sentiments += str(ent["sentiment_score"]) + SEPARATOR
        result['summary'] = highlights
        result['sentiment'] = sentiments
        return result


class FinancialTimes(Logger):
    """FT Times Headline API aggregator."""
    __url = "http://api.ft.com/content/search/v1"
    __qstr = {"apiKey": API_FT}
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
                components_dict = {'apiUrl': result['apiUrl'],
                                   'publishDate': result['lifecycle']['lastPublishDateTime'][:10],
                                   'summary': result['summary']['excerpt']}
                if self.__title:
                    components_dict['title'] = result['title']['title']
                final_result.append(components_dict)
            except KeyError as exp:
                self.add('ERROR', "Key Missing in result. {}".format(exp))
        self.add('INFO', "Final FT get_final_components.")
        return final_result


class DataArrangement(Logger):
    """Mainly for converting the JSON response to pandas DataFrame."""

    def __init__(self, source):
        super().__init__(DataArrangement.__name__)
        self.__data = source.get_final_components()

    def get_summary_date_api(self, parameters=None, title=True):
        """:return pandas df with summary, title and other components"""
        self.add('INFO', "SUMMARY/DATE/API called."
                         " With title as {}.".format(title))
        data = pd.DataFrame(data=self.__data,
                            columns=['apiUrl', 'publishDate', 'summary', 'title', 'sentiment'])
        if title is False:
            return data.drop(['title'], axis=1)
        return data

    def get_summary_for_w2v(self, title=False):
        """:returns List with summary and title which are comma seperated."""
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


if __name__ == "__main__":
    params = {"symbols": "AAPL"}
    G = GoogleNewsApi('AAPL')
    S = G.get_final_components()

    C = DataArrangement(G)
    final_c = C.get_summary_date_api()
    print(final_c)


