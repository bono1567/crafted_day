import elasticsearch
from elasticsearch import Elasticsearch

import Constants
from Harvester.StockPriceHarvester.DataRetriever import AlphaVantageStocks, AlphaVantageTechnicalIndicators
import pandas as pd
import time
from LoggerApi.Logger import Logger
import os

features = Constants.FEATURES


def get_code_symbol_name(stock_indicator):
    dirs = [str(folder) for folder in os.path.dirname(os.getcwd()).split("\\")]
    ROOT = ""
    for folder in dirs:
        ROOT = ROOT + str(folder) + "\\"
        if str(folder).find('crafted') != -1:
            break
    data = pd.read_csv(ROOT + "\\Harvester\\resources\\Final_Listing_2020_Real.csv")
    try:
        stock_indicator = int(stock_indicator)
        data = data[data['Security Code'] == stock_indicator]
    except ValueError:
        data = data[data['Security Id'] == stock_indicator]
    if 0 == data.size:
        return '', '', ''
    return data['Security Code'].values[0], data['Security Id'].values[0], data['Security Name'].values[0]


"""This gives us the data from AlphaVantage feature-wise"""


class ArrangedData:
    """interval: Day, Week, Minutes
        time_period is in mins, mainly for intraday"""

    def __init__(self, interval):
        self.__interval = interval

    @staticmethod
    def __trend_generator(data):
        trend = []
        for difference in data.close.diff():
            if difference > 0:
                trend.append('UP')
            elif difference < 0:
                trend.append('DOWN')
            else:
                trend.append('NC')

        return trend

    def __fetch_helper(self, sym, sample_number, time_period=60, series_type="open", nbdu=2, nbdd=2):
        stock_instance = AlphaVantageStocks(sym)
        stock_prices = stock_instance.fetch(sample_number, self.__interval)
        stock_prices['time'] = stock_prices['timestamp']
        stock_prices.drop('timestamp', axis=1, inplace=True)
        stock_prices['trend'] = self.__trend_generator(stock_prices)

        indicator_instance = AlphaVantageTechnicalIndicators(sym)
        for feature in features:
            if feature is 'VWAP' and isinstance(self.__interval, str):
                continue
            current = indicator_instance.get_trend(feature, sample_number, time_period=time_period,
                                                   series_type=series_type, interval=self.__interval,
                                                   nbdd=nbdd, nbdu=nbdu)
            stock_prices = pd.merge(stock_prices, current, on='time')
            time.sleep(10)

        return stock_prices

    def fetch_all(self, symbols, sample_number, time_period=60, series_type="open", nbdu=2, nbdd=2):
        """Return data of each stocks in a list of data-frames"""
        stocks_data = []

        for sym in symbols:
            stocks_data.append(self.__fetch_helper(sym, sample_number, time_period, series_type, nbdu, nbdd))

        return stocks_data

    def fetch(self, sym, sample_number, time_period=60, series_type="open", nbdu=2, nbdd=2):
        return self.__fetch_helper(sym, sample_number, time_period, series_type, nbdu, nbdd)


"""Fetch Historical Data from ES or the live Alpha-Vantage APIs"""


class FetchHistFromES(Logger):
    def __init__(self, interval, time_period):
        super().__init__(FetchHistFromES.__name__, "LOGS_FETCH_FOR_MODEL")
        self.INTERVAL = interval
        self.TIME_PERIOD = time_period
        try:
            self.es = Elasticsearch(Constants.ES_URL, port=Constants.ES_PORT, retry_on_timeout=True,
                                    sniff_on_start=True,
                                    sniff_on_connection_fail=True,
                                    sniffer_timeout=60)
        except elasticsearch.exceptions.TransportError:
            self.add("ERROR", "ES host is down.")

    def __set_vwap(self, stock_indicator):
        tech_indicator = AlphaVantageTechnicalIndicators(stock_indicator)
        self.add("INFO", "VWAP in AlphaVantage is unstable, using MFI.")
        self.vwap = tech_indicator.get_trend('VWAP', sample_number=100 * 24, interval=60)
        if self.vwap.shape is (2, 1):
            self.add("ERROR", "VWAP is null.")
            self.vwap = None

    def get_stock_data(self, stock_indicator, from_live=True):
        other_data = get_code_symbol_name(stock_indicator)
        if from_live:
            model = ArrangedData(self.INTERVAL)
            try:
                stock_data = model.fetch(stock_indicator + '.BSE', self.TIME_PERIOD)
                stock_data['code'] = other_data[0]
                stock_data['symbol'] = other_data[1]
                stock_data['security_name'] = other_data[2]
                if 'VWAP' in Constants.FEATURES:
                    self.__set_vwap(stock_indicator + '.BSE')
            except KeyError:
                self.add("ERROR", "The data doesn't exist in Alpha-Vantage DB. Symbol Used: {}. Company: {}"
                         .format(stock_indicator, other_data[2]))
                try:
                    stock_data = model.fetch(str(other_data[0]) + '.BSE', self.TIME_PERIOD)
                    stock_data['code'] = other_data[0]
                    stock_data['symbol'] = other_data[1]
                    stock_data['security_name'] = other_data[2]
                    if 'VWAP' in Constants.FEATURES:
                        self.__set_vwap(str(other_data[0]) + '.BSE')
                except KeyError:
                    self.add("ERROR", "The data doesn't exist in Alpha-Vantage DB. Symbol Used: {}. Company: {}"
                             .format(other_data[0], other_data[2]))
                    stock_data = None
            return stock_data
        else:
            query = Constants.SEARCH_FOR_HIST_STOCK_DATA
            query["query"]["bool"]["filter"]["term"]["code"] = other_data[0]
            try:
                if self.INTERVAL is 'D':
                    stock_data = self.es.search(index=Constants.HIST_TECH_DATA_DAILY_INDEX, body=query, size=1500)
                else:
                    stock_data = self.es.search(index=Constants.HIST_TECH_DATA_WEEKLY_INDEX, body=query, size=1500)
            except AttributeError:
                return self.get_stock_data(stock_indicator, from_live=True)
            self.add("INFO", "Data successfully fetched from ES for {}.".format(other_data[2]))
            try:
                return self.__refine_data_to_csv(stock_data['hits']['hits'])
            except KeyError:
                self.add("ERROR", "The data is not present in ES index, redirecting to the live approach")
            if 'VWAP' in Constants.FEATURES:
                try:
                    self.__set_vwap(stock_indicator + '.BSE')
                except KeyError:
                    self.add("ERROR", "FOR VWAP changing the code to: {}".format(other_data[0]))

            return self.get_stock_data(stock_indicator, True)

    def __refine_data_to_csv(self, json_data):
        all_json = {}
        index = 0
        for hit in json_data:
            all_json[str(index)] = hit["_source"]
            index += 1
        final_data = pd.DataFrame.from_dict(all_json, orient='index')
        final_data['time'] = pd.to_datetime(final_data['time'])
        final_data.sort_values(by='time', ascending=False, inplace=True)
        self.add("INFO", "Conversion from JSON to CSV done.")
        return final_data.iloc[:self.TIME_PERIOD]


# if __name__ == '__main__':
#     # A = ArrangedData('D')
#     # B = A.fetch("506480.BSE", 365 * 3)
#     # print(B.shape)
#
#     A = FetchHistFromES('D', 365)
#     # print(A.get_stock_data("MTNL").head())
#     B = A.get_stock_data("TITAN", True).head()
#     print("DONE")