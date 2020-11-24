from elasticsearch import Elasticsearch
import os
import pandas as pd
import Constants
from Harvester.StockPriceHarvester.DataArrangement import ArrangedData
from LoggerApi.Logger import Logger
from Harvester import Utils

"""This will for mainly long term investment model. Hence not be used frequently."""


class VantageToES(Logger):
    def __init__(self, interval='D', time=365):
        self.interval = interval
        super().__init__(VantageToES.__name__, "TEMP_ES_LOG")
        self.model = ArrangedData(interval)
        self.es = Elasticsearch(Constants.ES_URL, port=Constants.ES_PORT, retry_on_timeout=True, sniff_on_start=True,
                                sniff_on_connection_fail=True,
                                sniffer_timeout=60)
        self.time = time
        self.__from_vantage_to_es()

    def __from_vantage_to_es(self):
        code_list, symbol_list, security_name = Utils.join_nse_bse_listing(os.path.dirname((os.getcwd())))
        # Due to the everyday API restriction we will process 100 per day
        code_list = code_list[:Constants.INSERTION_OFFSET]
        symbol_list = symbol_list[:Constants.INSERTION_OFFSET]
        security_name = security_name[:Constants.INSERTION_OFFSET]
        for i in range(len(code_list)):
            try:
                stock_data = self.model.fetch(str(code_list[i]) + '.BSE', self.time)
                stock_data['code'] = code_list[i]
                stock_data['symbol'] = symbol_list[i]
                stock_data['security_name'] = security_name[i]
            except KeyError:
                self.add("ERROR", "The data doesn't exist in Alpha-Vantage DB. Symbol Used: {}. Company: {}".
                         format(code_list[i], security_name[i]))
                try:
                    stock_data = self.model.fetch(str(symbol_list[i]) + '.BSE', self.time)
                    stock_data['code'] = code_list[i]
                    stock_data['symbol'] = symbol_list[i]
                    stock_data['security_name'] = security_name[i]
                except KeyError:
                    self.add("ERROR", "The data doesn't exist in Alpha-Vantage DB with alternative approach as well."
                                      " Symbol Used: {}. Company: {}".
                             format(symbol_list[i], security_name[i]))
                    stock_data = None
            self.__insert_into_es(stock_data)

    def __insert_into_es(self, stock_data):
        if stock_data is None:
            return
        # naming = stock_data.iloc[0]['symbol']
        for (_, item) in stock_data.to_dict(orient='index').items():
            if self.interval is 'D':
                self.es.index(index=Constants.HIST_TECH_DATA_DAILY_INDEX, body=item)
            elif self.interval is 'W':
                self.es.index(index=Constants.HIST_TECH_DATA_WEEKLY_INDEX, body=item)

        self.add("INFO", "Insertion into the respective index was successful.Security Name: {}".
                 format(stock_data['security_name'][0]))


if __name__ == '__main__':
    """Insert the last 4 years data."""
    VantageToES(time=365 * 3)
    data = pd.read_csv(os.path.dirname((os.getcwd())) + "\\resources\\Final_listing_2020.csv")
    data = data.iloc[Constants.INSERTION_OFFSET:]
    data.to_csv(os.path.dirname((os.getcwd())) + "\\resources\\Final_listing_2020.csv", index=False)
    print("DONE")
