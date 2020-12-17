"""Saves it in the resources folder. The EQUITY data. """
import pandas as pd
from Harvester.StockPriceHarvester.NSEToolsHarvester import FetchData


def nse_listing():
    """Getting the list of symbols from the listing. """
    listing = pd.read_csv('./resources/NSE_Listing_2020.csv', header=0)
    listing['SYMBOL'] = listing['SYMBOL']
    return listing['SYMBOL'].tolist()


if __name__ == '__main__':
    MODEL = FetchData.FetchNSEData(5)
    MODEL.save_daily_data()
