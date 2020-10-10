import pandas as pd

from Harvester.HeadlineHarvester.DataArrangement import FTArrangeWithWords
from Harvester.StockPriceHarvester.DataRetriever import AlphaVantageStocks

"""DataWeaver will return the headline with the date and trend with the respective headline. 
Only applicable for AlphaVantage interface."""


class DataWeaver:
    def __init__(self, words, stock):
        self.model_headlines = FTArrangeWithWords(words)
        self.model_stocks = AlphaVantageStocks(stock)
        self.sym = [stock]

    @staticmethod
    def __trend_generator(generated_data):
        trend = []
        for difference in generated_data.close.diff():
            if difference > 0:
                trend.append('UP')
            elif difference < 0:
                trend.append('DOWN')
            else:
                trend.append('NC')

        return trend

    def __get_the_data__(self):
        current_data = self.model_stocks.fetch(365.25 * 4, 'D')
        current_data['trend'] = self.__trend_generator(current_data)
        return current_data

    def __weave__(self):
        current_data = pd.DataFrame()
        temp_data = self.__get_the_data__()
        if 'time' in temp_data.columns:
            current_data['time'] = temp_data['time'].copy()
        else:
            current_data['time'] = temp_data['timestamp'].copy()

        current_data['trend'] = temp_data['trend']
        del temp_data
        return current_data

    def fetch(self, title=False):
        return pd.merge(self.model_headlines.get_summary(title), self.__weave__(), on='time')


"""if __name__ == '__main__':
    A = DataWeaver(['India', 'Modi', 'Data'], '500325.BSE')
    # data = A.fetch(True)"""
