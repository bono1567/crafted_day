import pandas as pd

from Harvester.HeadlineHarvester.DataArrangement import FTArrangeWithWords
from Harvester.StockPriceHarvester.DataRetriever import AlphaVantageStocks

"""DataWeaver will return the headline with the date and trend with the respective headline"""


class DataWeaver:
    def __init__(self, words, stock):
        self.model_headlines = FTArrangeWithWords(words)
        self.model_stocks = AlphaVantageStocks(stock)
        self.sym = [stock]

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

    def __get_the_data__(self):
        data = self.model_stocks.fetch(365.25 * 4, 'D')
        data['trend'] = self.__trend_generator(data)
        return data

    def __weave__(self):
        data = pd.DataFrame()
        temp_data = self.__get_the_data__()
        if 'time' in temp_data.columns:
            data['time'] = temp_data['time'].copy()
        else:
            data['time'] = temp_data['timestamp'].copy()

        data['trend'] = temp_data['trend']
        del temp_data
        return data

    def fetch(self, title=False):
        return pd.merge(self.model_headlines.getSummary(title), self.__weave__(), on='time')


"""if __name__ == '__main__':
    A = DataWeaver(['India', 'Modi', 'Cars'], 'NSE:TATAMOTORS')
    data = A.fetch(True)

    print(np.unique(data['trend']))"""
