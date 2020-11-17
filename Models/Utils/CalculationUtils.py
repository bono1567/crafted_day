import Constants
from datetime import datetime
from Harvester.StockPriceHarvester.DataArrangement import FetchHistFromES
from LoggerApi.Logger import Logger
import pandas as pd

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


def get_max_min_points(data, column_name):
    if column_name not in data.columns.values:
        raise KeyError
    max_min_index = []
    data_list = data[column_name].values
    index_list = data['time'].values
    size = data.shape[0]
    if size <= 3:
        return data[['time', column_name]]
    for i in range(1, size - 1):
        if data_list[i - 1] < data_list[i] and data_list[i] > data_list[i + 1]:  # Maxima point
            max_min_index.append(index_list[i])
        if data_list[i - 1] > data_list[i] and data_list[i] < data_list[i + 1]:  # Minima point
            max_min_index.append(index_list[i])

    return data[['time', column_name]][data['time'].isin(max_min_index)]


"""
We will implement the Modified Schiff's pitchfork
"""


def get_date_midpoint(date_1, date_2):
    return date_1 + (date_2 - date_1) / 2


def get_mid_point(coordinate_1, coordinate_2):
    return {'y': (coordinate_1['y'] + coordinate_2['y']) / 2,
            'x': get_date_midpoint(coordinate_1['x'], coordinate_2['x'])}


def get_slope(mid_12, mid_23):
    return (mid_23['y'] - mid_12['y']) / (mid_23['x'] - mid_12['y'])


def get_in_days(dt):
    dt = pd.Timestamp(dt).to_pydatetime()
    days = dt - datetime(1, 1, 1, 0, 0, 0, 0)
    return days.days


class PitchFork:
    __b = {}

    def __init__(self, points_x, points_y, mode='ModSchiff'):
        self.__point_1 = {'x': points_x[0], 'y': points_y[0]}
        self.__point_2 = {'x': points_x[1], 'y': points_y[1]}
        self.__point_3 = {'x': points_x[2], 'y': points_y[2]}
        if mode == 'ModSchiff':
            self.__mid_12 = get_mid_point(self.__point_1, self.__point_2)
            self.__mid_23 = get_mid_point(self.__point_2, self.__point_3)
            self.__M = get_slope(self.__mid_12, self.__mid_23)
            self.__m1 = get_mid_point(self.__mid_23, self.__point_3)
            self.__m2 = get_mid_point(self.__point_2, self.__mid_23)
            self.__b['UP'] = self.__get_b_of_line(self.__point_3)
            self.__b['DN'] = self.__get_b_of_line(self.__point_2)
            self.__b['UPM'] = self.__get_b_of_line(self.__m1)
            self.__b['DNM'] = self.__get_b_of_line(self.__m2)
            self.__b['MID'] = self.__get_b_of_line(self.__mid_23)

    def __get_b_of_line(self, coordinate):
        return coordinate['y'] - get_in_days(coordinate['x']) * self.__M

    def get_all(self):
        return {'mid_23': self.__mid_23, 'mid_12': self.__mid_12, 'M': self.__M, 'm1': self.__m1, 'm2': self.__m2,
                'b': self.__b}

    def check_price_state(self, point_x, point_y):
        # Put condition for checking where the current price lies. To signal BUY/SELL
        if (self.__M * get_in_days(point_x) + self.__b['UP']) <= point_y:
            return 0
        if (self.__M * get_in_days(point_x) + self.__b['UPM']) >= point_y:
            return 1
        if (self.__M * get_in_days(point_x) + self.__b['MID']) >= point_y:
            return 2
        if (self.__M * get_in_days(point_x) + self.__b['DNM']) >= point_y:
            return 3
        if (self.__M * get_in_days(point_x) + self.__b['DN']) >= point_y:
            return 4
        return 5


if __name__ == '__main__':
    A = FetchHistFromES('D', 365)
    B = A.get_stock_data("TITAN", False)
    sample1, sample2 = B['time'].values[0], B['time'].values[5]
    # print(sample1)
    # print(sample2)
    # print(get_date_midpoint(sample2, sample1))
    print(get_in_days(sample1))
