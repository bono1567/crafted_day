"""The state creation via models for the RL."""
import json

import numpy as np
import Constants
from Harvester.StockPriceHarvester.DataArrangement import FetchHistFromES
from LoggerApi.Logger import Logger
from Models.Utils.CalculationUtils import RiskRewardForStock, transcend_pitchfork, \
    get_trend_of_stock, get_momentum_from_macd, get_dow_check_correlation
from VisualisationSector.Graphs import VisualAnalysis


def change_time_of_pitchfork(pitchfork_data):
    """Time zone changer"""
    pitchfork_data['mid_23']['x'] = np.datetime_as_string(
        pitchfork_data['mid_23']['x'], timezone='local')
    pitchfork_data['mid_12']['x'] = np.datetime_as_string(
        pitchfork_data['mid_12']['x'], timezone='local')
    pitchfork_data['m1']['x'] = np.datetime_as_string(
        pitchfork_data['m1']['x'], timezone='local')
    pitchfork_data['m2']['x'] = np.datetime_as_string(
        pitchfork_data['m2']['x'], timezone='local')
    pitchfork_data['point_1']['x'] = np.datetime_as_string(
        pitchfork_data['point_1']['x'], timezone='local')
    pitchfork_data['point_2']['x'] = np.datetime_as_string(
        pitchfork_data['point_2']['x'], timezone='local')
    pitchfork_data['point_3']['x'] = np.datetime_as_string(
        pitchfork_data['point_3']['x'], timezone='local')
    pitchfork_data['convention'] = "True" if pitchfork_data['convention'] else "False"
    return pitchfork_data


class TechModel(Logger):
    """The state creator class and
    other analysis model calculation done in this class."""

    def __init__(self):
        self.interval = 'D'
        self.time_period = 365
        self.p_items = {}
        self.other_data = {}
        self.rr_rating, self.rr_ratio = (0, 0)
        super().__init__(TechModel.__name__, 'TECH_LOG')
        self.es_model = FetchHistFromES(self.interval, self.time_period)

    def analyse(self, stock_indicator, from_live=False, in_json=False):
        """The analyse a stock function."""
        graph_model = VisualAnalysis()
        annual_data = self.__get_stock_data(stock_indicator, from_live)

        self.p_items['price'] = graph_model.get_trend_line(
            annual_data, col_name='close', show_graph=False)
        self.p_items['cd_stick'] = graph_model.get_candlestick(
            annual_data, show_graph=False)
        self.p_items['volume'] = graph_model.get_volume_hist(
            annual_data, show_graph=False)
        if 'MACD' in annual_data.columns:
            self.add("INFO", "MACD Data exists.")
            self.p_items['MACD'] = graph_model.get_macd_plot(
                annual_data, show_graph=False)
        if 'MFI' in annual_data.columns:
            self.add("INFO", "MFI Data exists.")
            self.p_items['MFI'] = graph_model.get_trend_line(
                annual_data, col_name='MFI', show_graph=False)
        if 'ADX' in annual_data.columns:
            self.add("INFO", "MFI Data exists.")
            self.p_items['ADX'] = graph_model.get_trend_line(
                annual_data, col_name='ADX', show_graph=False)

        # Automate the selection of the pitch-fork points.
        pitchfork, pf_plot = transcend_pitchfork(annual_data)
        self.p_items['PITCH_FORK'] = graph_model.get_trend_line(
            annual_data, col_name='close', show_graph=False, p=pf_plot)
        self.p_items['price'] = graph_model.get_trend_line(
            annual_data, col_name='close', show_graph=False)
        graph_model.show_all(self.p_items, stock_indicator)

        # Trend check
        self.other_data['trend'] = get_trend_of_stock(
            annual_data.head(25 * Constants.MONTH_OF_TEST))

        # Momentum check with MACD hist.
        self.other_data['momentum'] = get_momentum_from_macd(
            annual_data.head(25 * Constants.MONTH_OF_TEST))

        # Dow's check with NIFTY
        self.other_data['dow_check'] = get_dow_check_correlation(
            annual_data[['time', 'adjusted_close']])
        self.add('INFO', 'Dow check complete.')

        # Expected profit and loss from PITCHFORK analysis
        y_for_all = pitchfork.get_y_for_all_lines(annual_data['time'].values[0])
        self.__set_risk_reward(y_for_all['DNM'], y_for_all['UP'], y_for_all['DN'])

        self.other_data['pitchfork'] = pitchfork.get_all()
        if in_json:
            return json.dumps(self.get_stats())
        return self.get_stats()

    def __get_stock_data(self, stock_indicator, from_live):
        """Fetch stock data from harvester."""
        return self.es_model.get_stock_data(stock_indicator, from_live)

    def __set_risk_reward(self, closed_value, expected_book_price, stop_loss_amount):
        """Set the risk reward for a particular stock."""
        rr_model = RiskRewardForStock()
        self.rr_rating = rr_model.get_rating(
            closed_value, expected_book_price, stop_loss_amount)
        self.rr_ratio = rr_model.ratio
        self.add("INFO", "R/R calculated: {:.4f} (Date of calculation: {})".format(
            self.rr_ratio, closed_value))

    def get_stats(self):
        """Returns a dict of all the attributes calculated.
        :returns 1. Pitchfork.
                 2. Trend
                 3. Momentum
                 4. Dow's Theory check
                 5. R/R"""

        self.add('INFO', "Fetching stats from analysis.")
        return {'pitchfork': change_time_of_pitchfork(self.other_data['pitchfork']),
                'trend': self.other_data['trend'],
                'dow_check': self.other_data['dow_check'],
                'rr': {'rr_rating': self.rr_rating,
                       'rr_ration': self.rr_ratio}}

# if __name__ == "__main__":
#     A = TechModel()
#     # A.analyse('TITAN')
#     print(A.analyse('PRESTIGE', from_live=True, in_json=True))
