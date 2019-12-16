import unittest
import pandas as pd

from Harvester.StockPriceHarvester.DataRetriever import AlphaVantageStocks

class AlphaVantageTest(unittest.TestCase):
    def setUp(self):
        self.test_class = AlphaVantageStocks("NSE:TATAMOTORS")

    def test_FetchLatestID(self):
        URL = "https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&outputsize=full&symbol=NSE:TATAMOTORS" \
              "&apikey=UA3OCB0CIG6WMCJ0&datatype=csv&interval=15min"
        self.assertTrue(pd.testing.assert_frame_equal(self.test_class.fetch_latest("ID", 15),
                                                      pd.read_csv(URL, nrows=1)) is None)

    def test_FetchID(self):
        URL = "https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&outputsize=full&symbol=NSE:TATAMOTORS" \
              "&apikey=UA3OCB0CIG6WMCJ0&datatype=csv&interval=15min"
        self.assertTrue(pd.testing.assert_frame_equal(self.test_class.fetch("ID", 10, 15),
                                                      pd.read_csv(URL, nrows=10)) is None)

    def test_FetchLatestOthers(self):
        URL = "https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&outputsize=full&symbol=NSE:TATAMOTORS" \
              "&apikey=UA3OCB0CIG6WMCJ0&datatype=csv"
        pd.read_csv(URL, nrows=1) #Refresh the API usage
        self.assertTrue(pd.testing.assert_frame_equal(self.test_class.fetch_latest("D"),
                                                        pd.read_csv(URL, nrows=1).head()) is None)

    def test_FetchOthers(self):
        URL = "https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&outputsize=full&symbol=NSE:TATAMOTORS" \
              "&apikey=UA3OCB0CIG6WMCJ0&datatype=csv"
        self.assertTrue(pd.testing.assert_frame_equal(self.test_class.fetch("D",10),
                                                        pd.read_csv(URL, nrows=10)) is None)

if __name__ == '__main__':
    unittest.main()





