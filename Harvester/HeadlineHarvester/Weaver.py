"""DataWeaver will return the headline with the date and
trend with the respective headline.
Only applicable for AlphaVantage interface."""
import pandas as pd

from Harvester.HeadlineHarvester.DataArrangement import FTArrangeWithWords
from Harvester.StockPriceHarvester.DataRetriever import AlphaVantageStocks


def trend_generator(generated_data):
    """It to see if it is a up compared to the previous pricing.
    :return List of trend with a combination of UP/DOWN/NC"""
    trend = []
    for difference in generated_data.close.diff():
        if difference > 0:
            trend.append('UP')
        elif difference < 0:
            trend.append('DOWN')
        else:
            trend.append('NC')

    return trend


class DataWeaver:
    """Weave the headline data with the trend data and return the data when initialized."""
    def __init__(self, words, stock):
        self.model_headlines = FTArrangeWithWords(words)
        self.model_stocks = AlphaVantageStocks(stock)
        self.sym = [stock]

    def __get_the_data__(self):
        """:return Pandas DF. the stock data for the last 4 years from AVantage + the trend."""
        current_data = self.model_stocks.fetch(365.25 * 4, 'D')
        current_data['trend'] = trend_generator(current_data)
        return current_data

    def __weave__(self):
        """:return Df with trend and timestamp columns for a stock."""
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
        """Fetches the Headline data and merges it with the trend.
        :return PD of headline summary, title (if title=True), trend and time stamp columns.  """
        return pd.merge(self.model_headlines.get_summary(title), self.__weave__(), on='time')


# """if __name__ == '__main__':
#     A = DataWeaver(['India', 'Modi', 'Data'], '500325.BSE')
#     # data = A.fetch(True)"""
