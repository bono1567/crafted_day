"""Alpha-vantage data arrangement"""
import time
import os
import elasticsearch
from elasticsearch import Elasticsearch
import pandas as pd

from Harvester.HeadlineHarvester.Weaver import trend_generator
from Harvester.StockPriceHarvester.DataRetriever import AlphaVantageStocks, AlphaVantageTechnicalIndicators
from LoggerApi.Logger import Logger
import Constants


FEATURES = Constants.FEATURES


def get_code_symbol_name(stock_indicator):
    """Returns the list of symbols coinciding with NSE."""
    dirs = [str(folder) for folder in os.path.dirname(os.getcwd()).split("\\")]
    root = ""
    for folder in dirs:
        root = root + str(folder) + "\\"
        if str(folder).find('crafted') != -1:
            break
    data = pd.read_csv(root + "\\Harvester\\resources\\Final_Listing_2020_Real.csv")
    try:
        stock_indicator = int(stock_indicator)
        data = data[data['Security Code'] == stock_indicator]
    except ValueError:
        data = data[data['Security Id'] == stock_indicator]
    if data.size == 0:
        return '', '', ''
    return [data['Security Code'].values[0],
            data['Security Id'].values[0], data['Security Name'].values[0]]


class ArrangedData:
    """This gives us the data from AlphaVantage feature-wise
    interval: Day, Week, Minutes
    time_period is in mins, mainly for intraday"""

    def __init__(self, interval):
        self.__interval = interval

    def __fetch_helper(self, sym, sample_number, time_period=60):
        stock_instance = AlphaVantageStocks(sym)
        stock_prices = stock_instance.fetch(sample_number, self.__interval)
        stock_prices['time'] = stock_prices['timestamp']
        stock_prices.drop('timestamp', axis=1, inplace=True)
        stock_prices['trend'] = trend_generator(stock_prices)

        indicator_instance = AlphaVantageTechnicalIndicators(sym)
        for feature in FEATURES:
            if feature == 'VWAP' and isinstance(self.__interval, str):
                continue
            current = indicator_instance.get_trend(feature, sample_number, time_period=time_period,
                                                   interval=self.__interval)
            stock_prices = pd.merge(stock_prices, current, on='time')
            time.sleep(10)

        return stock_prices

    def fetch_all(self, symbols, sample_number, time_period=60):
        """Return data of each stocks in a list of data-frames"""
        stocks_data = []

        for sym in symbols:
            stocks_data.append(self.__fetch_helper(sym, sample_number, time_period))

        return stocks_data

    def fetch(self, sym, sample_number, time_period=60):
        """Fetch data for the stocks."""
        return self.__fetch_helper(sym, sample_number, time_period)


class FetchHistFromES(Logger):
    """Fetch Historical Data from ES or the live Alpha-Vantage APIs"""
    __vwap = None

    def __init__(self, interval, time_period):
        super().__init__(FetchHistFromES.__name__, "LOGS_FETCH_FOR_MODEL")
        self.interval = interval
        self.time_period = time_period
        try:
            self.elastic_search = Elasticsearch(Constants.ES_URL, port=Constants.ES_PORT,
                                                retry_on_timeout=True,
                                                sniff_on_start=True,
                                                sniff_on_connection_fail=True,
                                                sniffer_timeout=60)
        except elasticsearch.exceptions.TransportError:
            self.add("ERROR", "ES host is down.")

    def __set_vwap(self, stock_indicator):
        tech_indicator = AlphaVantageTechnicalIndicators(stock_indicator)
        self.add("INFO", "VWAP in AlphaVantage is unstable, using MFI.")
        self.__vwap = tech_indicator.get_trend('VWAP', sample_number=100 * 24, interval=60)
        if self.__vwap.shape == (2, 1):
            self.add("ERROR", "VWAP is null.")

    def get_stock_data(self, stock_indicator, from_live=True):
        """Fetch the stock data from ES or from AlphaVantage depends on from_live"""
        other_data = get_code_symbol_name(stock_indicator)
        if from_live:
            model = ArrangedData(self.interval)
            try:
                stock_data = model.fetch(stock_indicator + '.BSE', self.time_period)
                stock_data['code'] = other_data[0]
                stock_data['symbol'] = other_data[1]
                stock_data['security_name'] = other_data[2]
                if 'VWAP' in Constants.FEATURES:
                    self.__set_vwap(stock_indicator + '.BSE')
            except KeyError:
                self.add("ERROR",
                         "The data doesn't exist in Alpha-Vantage DB."
                         " Symbol Used: {}. Company: {}"
                         .format(stock_indicator, other_data[2]))
                try:
                    stock_data = model.fetch(str(other_data[0]) + '.BSE', self.time_period)
                    stock_data['code'] = other_data[0]
                    stock_data['symbol'] = other_data[1]
                    stock_data['security_name'] = other_data[2]
                    if 'VWAP' in Constants.FEATURES:
                        self.__set_vwap(str(other_data[0]) + '.BSE')
                except KeyError:
                    self.add("ERROR", "The data doesn't exist in Alpha-Vantage DB."
                                      " Symbol Used: {}. Company: {}"
                             .format(other_data[0], other_data[2]))
                    stock_data = None
            stock_data['time'] = pd.to_datetime([str(x) for x in stock_data['time']])
            return stock_data

        query = Constants.SEARCH_FOR_HIST_STOCK_DATA
        query["query"]["bool"]["filter"]["term"]["code"] = other_data[0]
        try:
            if self.interval == 'D':
                stock_data = self.elastic_search.search(
                    index=Constants.HIST_TECH_DATA_DAILY_INDEX, body=query)
            else:
                stock_data = self.elastic_search.search(
                    index=Constants.HIST_TECH_DATA_WEEKLY_INDEX, body=query)
        except AttributeError:
            return self.get_stock_data(stock_indicator, from_live=True)
        self.add("INFO", "Data successfully fetched from ES for {}.".format(other_data[2]))
        try:
            return self.__refine_data_to_csv(stock_data['hits']['hits'])
        except KeyError:
            self.add("ERROR", "The data not present in ES index, redirecting to the live approach")
        if 'VWAP' in Constants.FEATURES:
            try:
                self.__set_vwap(stock_indicator + '.BSE')
            except KeyError:
                self.add("ERROR", "FOR VWAP changing the code to: {}".format(other_data[0]))

        return self.get_stock_data(stock_indicator, True)

    def __refine_data_to_csv(self, json_data):
        """Convert JSON to CSV"""
        all_json = {}
        index = 0
        for hit in json_data:
            all_json[str(index)] = hit["_source"]
            index += 1
        final_data = pd.DataFrame.from_dict(all_json, orient='index')
        final_data['time'] = pd.to_datetime(final_data['time'])
        final_data.sort_values(by='time', ascending=False, inplace=True)
        self.add("INFO", "Conversion from JSON to CSV done.")
        return final_data.iloc[:self.time_period]

# if __name__ == '__main__':
#     # A = ArrangedData('D')
#     # B = A.fetch("506480.BSE", 365 * 3)
#     # print(B.shape)
#
#     A = FetchHistFromES('D', 365)
#     # print(A.get_stock_data("MTNL").head())
#     B = A.get_stock_data("TITAN", False)
#     print(B.shape)
#     print("DONE")
