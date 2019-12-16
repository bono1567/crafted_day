import time

import pandas as pd
import numpy as np

URL = "https://www.alphavantage.co/query?function={}&outputsize=full&symbol={}&apikey={}&datatype=csv"
"""
This is the data harvester class from the AlphaVantage APIs
key: API key
uri: API call URI
key_map: Stock timeframe
"""


class AlphaVantageStocks:
    __key = "UA3OCB0CIG6WMCJ0"
    __uri = URL
    __key_map = {
        "D": "TIME_SERIES_DAILY_ADJUSTED",
        "ID": "TIME_SERIES_INTRADAY",
        "W": "TIME_SERIES_WEEKLY_ADJUSTED",
        "M": "TIME_SERIES_MONTHLY_ADJUSTED"
    }

    def __init__(self, sym):
        self.__symbol = sym

    def fetch_latest(self, interval):
        if interval in [1, 5, 15, 30, 60]:
            interval = str(interval) + "min"
            self.__uri = URL + "&interval=" + interval
            interval = 'ID'

        print(self.__uri.format(self.__key_map[interval], self.__symbol, self.__key))
        return pd.read_csv(self.__uri.format(self.__key_map[interval], self.__symbol, self.__key), nrows=1)

    def fetch(self, size, interval):
        if interval in [1, 5, 15, 30, 60]:
            interval = str(interval) + "min"
            self.__uri = URL + "&interval=" + interval
            interval = 'ID'

        print(self.__uri.format(self.__key_map[interval], self.__symbol, self.__key))
        return pd.read_csv(self.__uri.format(self.__key_map[interval], self.__symbol, self.__key), nrows=size)


"function=STOCH&symbol=MSFT&interval=daily&apikey=demo"
COM_URL = "https://www.alphavantage.co/query?"
SMA_EMA_RSI_URL = COM_URL + "function={}&symbol={}&interval={}&time_period={}&series_type={}&apikey={}&datatype=csv"
MACD_URL = COM_URL + "function=MACD&symbol={}&interval={}&series_type={}&apikey={}&datatype=csv"
ADX_CCI_AROON_URL = COM_URL + "function={}&symbol={}&interval={}&time_period={}&apikey={}&datatype=csv"
BB_URL = COM_URL + "function=BBANDS&symbol={}&interval={}&time_period={}&series_type={}&nbdevup={}&nbdevdn={}&apikey={}" \
                   "&datatype=csv"
VWAP_AD_OBV_STOCH_URL = COM_URL + "function={}&symbol={}&interval={}&apikey={}&datatype=csv"


class AlphaVantageTechnicalIndicators:
    __features = ['SMA', 'EMA', 'VWAP', 'MACD', 'STOCH', 'RSI', 'ADX', 'CCI', 'AROON', 'BBANDS', 'AD', 'OBV']
    __key = "UA3OCB0CIG6WMCJ0"
    __interval_map = {"D": "daily", "W": "weekly", "M": "monthly"}

    def __init__(self, symbol):
        self.__symbol = symbol

    def get_trend(self, function, sample_number, interval="D", time_period=60, series_type="open", nbdu=2, nbdd=2):
        time_period = str(time_period)

        if interval in [1, 5, 15, 30, 60]:
            tp = str(interval) + "min"
        else:
            tp = self.__interval_map[interval]

        if function in ['SMA', 'EMA', 'RSI']:
            print(SMA_EMA_RSI_URL.format(function, self.__symbol, tp, time_period, series_type, self.__key))
            return pd.read_csv(
                SMA_EMA_RSI_URL.format(function, self.__symbol, tp, time_period, series_type, self.__key),
                nrows=sample_number)

        if function in ['VWAP', 'AD', 'OBV', 'STOCH']:
            if function is 'VWAP':
                if tp in ['daily', 'weekly', 'monthly']:
                    raise Exception("Give interval in minutes")
            print(VWAP_AD_OBV_STOCH_URL.format(function, self.__symbol, tp, self.__key))
            return pd.read_csv(
                VWAP_AD_OBV_STOCH_URL.format(function, self.__symbol, tp, self.__key),
                nrows=sample_number)

        if function in ['ADX', 'CCI', 'AROON']:
            print(ADX_CCI_AROON_URL.format(function, self.__symbol, tp, time_period, self.__key))
            return pd.read_csv(
                ADX_CCI_AROON_URL.format(function, self.__symbol, tp, time_period, self.__key),
                nrows=sample_number)

        if function is 'MACD':
            print(MACD_URL.format(self.__symbol, tp, series_type, self.__key))
            return pd.read_csv(
                MACD_URL.format(self.__symbol, tp, series_type, self.__key),
                nrows=sample_number)

        if function is 'BBANDS':
            nbdu = str(nbdu)
            nbdd = str(nbdd)
            print(BB_URL.format(self.__symbol, tp, time_period, series_type, nbdu, nbdd, self.__key))
            return pd.read_csv(
                BB_URL.format(self.__symbol, tp, time_period, series_type, nbdu, nbdd, self.__key),
                nrows=sample_number)


"""if __name__ == '__main__':
    A = AlphaVantageTechnicalIndicators('NSE:TATAMOTORS')
    B = AlphaVantageStocks('NSE:TATAMOTORS')
    features = ['SMA', 'EMA', 'MACD', 'STOCH', 'RSI', 'ADX', 'CCI', 'AROON', 'BBANDS', 'AD', 'OBV']
    answers = []
    for function in features:
        answers.append(A.get_trend(function, 10, interval='D'))
        if function is 'STOCH' or function is 'BBANDS':
            time.sleep(60.0)

    print(B.fetch(10, 15).head())
    for ans in answers:
        print(ans.head())"""