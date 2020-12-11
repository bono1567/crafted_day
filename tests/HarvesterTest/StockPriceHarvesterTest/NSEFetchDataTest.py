"""This is a unit test case for NSE data a harvester"""
import unittest

from mock import patch
from pandas.errors import EmptyDataError
from Harvester.StockPriceHarvester.NSEToolsHarvester.FetchData import FetchNSEData


class MyTestCase(unittest.TestCase):
    """Unit test case for NSE harvester."""
    model = FetchNSEData()

    def test_save_daily_invalid_code(self):
        """Test wrong stock symbol exception functionality."""
        with self.assertRaises(EmptyDataError) as context:
            self.model.save_daily_data(['ABC'], False)

        self.assertEqual("NO SYMBOLS TO PROCESS", str(context.exception))

    @patch('nsetools.Nse.get_quote')
    def test_successful_log(self, m_r):
        """Test the save from NSE source functionality"""
        m_r.return_value = dict(pricebandupper=200.95, symbol='TATAMOTORS',
                                applicableMargin=27.15,
                                bcEndDate='09-AUG-16', totalSellQuantity=None,
                                adhocMargin=None,
                                companyName='Tata Motors Limited', marketType='N',
                                exDate='18-JUL-16',
                                bcStartDate='20-JUL-16', css_status_desc='Listed',
                                dayHigh=182.7,
                                basePrice=182.7, securityVar=23.65, pricebandlower=164.45,
                                sellQuantity5=None,
                                sellQuantity4=None, sellQuantity3=None,
                                cm_adj_high_dt='15-JAN-20',
                                sellQuantity2=None, dayLow=176.4, sellQuantity1=None,
                                quantityTraded=38368777.0,
                                pChange='-2.60', totalTradedValue=68423.04,
                                deliveryToTradedQuantity=18.74,
                                totalBuyQuantity=20680.0, averagePrice=178.33,
                                indexVar=None, cm_ffm=31818.9,
                                purpose='DIVIDEND - RE 0.20/- PER SHARE', buyPrice2=None,
                                secDate='10-Dec-2020 00:00:00', buyPrice1=177.6, high52=201.7,
                                previousClose=182.7, ndEndDate=None, low52=63.5,
                                buyPrice4=None, buyPrice3=None,
                                recordDate=None, deliveryQuantity=7190829.0, buyPrice5=None,
                                priceBand='No Band', extremeLossMargin=3.5,
                                cm_adj_low_dt='24-MAR-20',
                                varMargin=23.65, sellPrice1=None, sellPrice2=None,
                                totalTradedVolume=38368777.0,
                                sellPrice3=None, sellPrice4=None, sellPrice5=None,
                                change='-4.75',
                                surv_indicator=None, ndStartDate=None, buyQuantity4=None,
                                isExDateFlag=False,
                                buyQuantity3=None, buyQuantity2=None,
                                buyQuantity1=20680.0, series='EQ',
                                faceValue=2.0, buyQuantity5=None, closePrice=177.6, open=182.7,
                                isinCode='INE155A01022', lastPrice=177.95)
        result_dict = self.model.save_daily_data(['TATAMOTORS'], False)
        self.assertEqual(["TATAMOTORS"], result_dict['symbol'])
        self.assertNotIsInstance(result_dict['lastPrice'], str)
        self.assertEqual([7190829.0], result_dict['deliveryQuantity'])


if __name__ == '__main__':
    unittest.main()
