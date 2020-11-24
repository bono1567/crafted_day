import Constants
from datetime import datetime
from Harvester.StockPriceHarvester.DataArrangement import FetchHistFromES
from Harvester.Utils import get_max_min_points
from LoggerApi.Logger import Logger
import pandas as pd

from VisualisationSector.Graphs import VisualAnalysis

logger = Logger(__file__, 'CALCULATION_LOG')


class RiskRewardForStock:
    ratio = 0

    def get_ratio(self, amount_invested, expected_book_price, stop_loss_amount):
        if amount_invested > expected_book_price:
            logger.add("ERROR", "You are expecting a loss from your investment")
            return None
        if stop_loss_amount > amount_invested:
            logger.add("ERROR", "Your stop loss amount is greater than the amount invested.")
            return None
        self.ratio = (expected_book_price - amount_invested) / (amount_invested - stop_loss_amount)
        return self.ratio

    def get_rating(self, amount_invested, expected_book_price, stop_loss_amount):
        if self.ratio == 0:
            self.get_ratio(amount_invested, expected_book_price, stop_loss_amount)
        if self.ratio > 4.0:
            return Constants.HL
        if self.ratio > 3.0:
            return Constants.AL
        if self.ratio > 2.0:
            return Constants.AA
        return Constants.LH


"""
We will implement the Modified Schiff's pitchfork
"""


def get_date_midpoint(date_1, date_2):
    return date_1 + (date_2 - date_1) / 2


def get_mid_point(coordinate_1, coordinate_2):
    return {'y': (coordinate_1['y'] + coordinate_2['y']) / 2,
            'x': get_date_midpoint(coordinate_1['x'], coordinate_2['x'])}


def get_slope(mid_12, mid_23):
    denominator = (mid_23['x'] - mid_12['x']).astype('int64') * 1e-6
    return (mid_23['y'] - mid_12['y']) / denominator


def get_in_milliseconds(dt):
    dt = pd.Timestamp(dt).to_pydatetime()
    epoch = datetime.utcfromtimestamp(0)
    return (dt - epoch).total_seconds() * 1000.0


class PitchFork:
    __b = {}

    def __init__(self, points_x, points_y, mode='ModSchiff'):
        self.__point_1 = {'x': points_x[2], 'y': points_y[2]}
        self.__point_2 = {'x': points_x[1], 'y': points_y[1]}
        self.__point_3 = {'x': points_x[0], 'y': points_y[0]}
        convention = self.__point_2['y'] > self.__point_1['y']  # Min-Max-Min convention
        if mode == 'ModSchiff':
            self.__mid_12 = get_mid_point(self.__point_1, self.__point_2)
            self.__mid_23 = get_mid_point(self.__point_2, self.__point_3)
            self.__M = get_slope(self.__mid_12, self.__mid_23)
            self.__m1 = get_mid_point(self.__mid_23, self.__point_3)
            self.__m2 = get_mid_point(self.__point_2, self.__mid_23)
            if not convention :
                self.__b['UP'] = self.__get_b_of_line(self.__point_3)
                self.__b['DN'] = self.__get_b_of_line(self.__point_2)
                self.__b['UPM'] = self.__get_b_of_line(self.__m1)
                self.__b['DNM'] = self.__get_b_of_line(self.__m2)
                self.__b['MID'] = self.__get_b_of_line(self.__mid_23)
            else:
                self.__b['DN'] = self.__get_b_of_line(self.__point_3)
                self.__b['UP'] = self.__get_b_of_line(self.__point_2)
                self.__b['DNM'] = self.__get_b_of_line(self.__m1)
                self.__b['UPM'] = self.__get_b_of_line(self.__m2)
                self.__b['MID'] = self.__get_b_of_line(self.__mid_23)

    def __get_b_of_line(self, coordinate):
        return coordinate['y'] - get_in_milliseconds(coordinate['x']) * self.__M

    def get_all(self):
        return {'mid_23': self.__mid_23, 'mid_12': self.__mid_12, 'M': self.__M, 'm1': self.__m1, 'm2': self.__m2,
                'b': self.__b}

    def check_price_state(self, x, y):
        # Put condition for checking where the current price lies. To signal BUY/SELL
        if (self.__M * get_in_milliseconds(x) + self.__b['UP']) <= y:
            return 0
        if (self.__M * get_in_milliseconds(x) + self.__b['UPM']) >= y:
            return 1
        if (self.__M * get_in_milliseconds(x) + self.__b['MID']) >= y:
            return 2
        if (self.__M * get_in_milliseconds(x) + self.__b['DNM']) >= y:
            return 3
        if (self.__M * get_in_milliseconds(x) + self.__b['DN']) >= y:
            return 4
        return 5

    def get_y_for_all_lines(self, x):
        x = get_in_milliseconds(x)
        return {'UP': self.__M * x + self.__b['UP'],
                'UPM': self.__M * x + self.__b['UPM'],
                'MID': self.__M * x + self.__b['MID'],
                'DNM': self.__M * x + self.__b['DNM'],
                'DN': self.__M * x + self.__b['DN']}

    def get_plot(self, p=None, show_graph=False):
        graph_model = VisualAnalysis()
        p = graph_model.get_slope_for_pitch_fork(self.__M, self.__b, p)  # plot for slopes
        p = graph_model.get_line(self.__point_1, self.__point_2, p, colour='b')
        p = graph_model.get_line(self.__point_2, self.__point_3, p, colour='b')
        p = graph_model.get_line(self.__mid_12, self.__mid_23, p, show_graph=show_graph)

        logger.add('INFO', 'The Pitchfork graph is created.')

        return p


if __name__ == '__main__':
    A = FetchHistFromES('D', 365)
    B = A.get_stock_data("TITAN", False)
    max_min_points = get_max_min_points(B, 'close')
    point_x = max_min_points['time'].values
    point_y = max_min_points['close'].values
    model = PitchFork(point_x[:3], point_y[:3])
    details = model.get_all()
    print(details)
    print(model.get_y_for_all_lines(point_x[-1:][0]))
    model.get_plot()
