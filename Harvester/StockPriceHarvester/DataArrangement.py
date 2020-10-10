import Constants
from Harvester.StockPriceHarvester.DataRetriever import AlphaVantageStocks, AlphaVantageTechnicalIndicators
import pandas as pd
import time

features = Constants.FEATURES

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


if __name__ == '__main__':
    A = ArrangedData('D')
    B = A.fetch("506480.BSE", 365*3)
    # print(B.size)
    print(B.shape)
