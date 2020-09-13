import pandas as pd
from Harvester.StockPriceHarvester.NSEToolsHarvester import FetchData
"""TODO: Introduce the AlphaVantage Code as well. """


def nse_listing():
    listing = pd.read_csv('./resources/NSE_Listing_2020.csv', header=0)
    listing['SYMBOL'] = listing['SYMBOL']
    return listing['SYMBOL'].tolist()


if __name__ == '__main__':
    model = FetchData.FetchNSEData(5)
    model.save_daily_data()
