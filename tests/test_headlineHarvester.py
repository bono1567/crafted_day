"""Harvester Unit Tests."""
import unittest

from mock import patch
import pandas as pd

from Harvester.HeadlineHarvester.Weaver import DataWeaver


class TestHeadLineHarvester(unittest.TestCase):
    """Unit test for Headline Harvester from FT times."""

    @patch('Harvester.HeadlineHarvester.DataRetriever.FinancialTimes.get_final_components')
    @patch('Harvester.StockPriceHarvester.DataRetriever.AlphaVantageStocks.fetch')
    def test_weaver(self, mock_get_trend, mock_get_news):
        """API-JSON to CSV functionality test."""
        mock_get_news.return_value = [{'aspectSet': 'article',
                                       'apiUrl': 'https://api.test.test',
                                       'publishDate': '2020-11-24',
                                       'summary': 'TEST_SUMMARY_1',
                                       'title': 'TEST_TITLE_1'},
                                      {'aspectSet': 'article',
                                       'apiUrl': 'https://api.test.test1',
                                       'publishDate': '2020-11-25',
                                       'summary': 'TEST_SUMMARY_2',
                                       'title': 'TEST_TITLE_2'}]
        data = [['2020-11-24', 12.34], ['2020-11-25', 45.67]]
        mock_get_trend.return_value = pd.DataFrame(data, columns=['timestamp', 'close'])

        sample = DataWeaver(['India'], '504879.BSE')
        data = sample.fetch(True)

        self.assertEqual(data.shape, (2, 4))
        self.assertEqual(data['time'].tolist(), ['2020-11-24', '2020-11-25'])
        self.assertEqual(data['title'].tolist(), ['TEST_TITLE_1', 'TEST_TITLE_2'])


if __name__ == '__main__':
    unittest.main()
