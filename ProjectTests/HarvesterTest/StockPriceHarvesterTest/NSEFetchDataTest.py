import unittest

from Harvester.StockPriceHarvester.NSEToolsHarvester.FetchData import FetchNSEData
from pandas.errors import EmptyDataError


class MyTestCase(unittest.TestCase):
    model = FetchNSEData()

    def test_save_daily_invalid_code(self):
        with self.assertRaises(EmptyDataError) as context:
            self.model.save_daily_data(['ABC'])

        self.assertEqual("NO SYMBOLS TO PROCESS", str(context.exception))

    def test_successful_log(self):
        result_dict = self.model.save_daily_data(['TATAMOTORS'], False)
        self.assertEqual(["TATAMOTORS"], result_dict['symbol'])
        self.assertNotIsInstance(result_dict['lastPrice'], str)


if __name__ == '__main__':
    unittest.main()
