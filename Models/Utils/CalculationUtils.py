from bokeh.io import show

import Constants
from Harvester.StockPriceHarvester.DataArrangement import FetchHistFromES
from Harvester.Utils import get_max_min_points
from LoggerApi.Logger import Logger
import pandas as pd
import numpy as np

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
    return np.datetime64(dt, 'ns').astype('int64') * 1e-6


class PitchFork:
    __b = {}

    def __init__(self, points_x, points_y, mode='ModSchiff'):
        self.__point_1 = {'x': points_x[0], 'y': points_y[0]}
        self.__point_2 = {'x': points_x[1], 'y': points_y[1]}
        self.__point_3 = {'x': points_x[2], 'y': points_y[2]}
        self.__convention = self.__point_2['y'] > self.__point_3['y'] and self.__point_2['y'] > self.__point_1['y']
        if mode == 'ModSchiff':
            self.__mid_12 = get_mid_point(self.__point_1, self.__point_2)
            self.__mid_23 = get_mid_point(self.__point_2, self.__point_3)
            self.__M = get_slope(self.__mid_12, self.__mid_23)

            if not self.__convention:
                self.__m1 = get_mid_point(self.__mid_23, self.__point_3)
                self.__m2 = get_mid_point(self.__point_2, self.__mid_23)
            else:
                self.__m2 = get_mid_point(self.__mid_23, self.__point_3)
                self.__m1 = get_mid_point(self.__point_2, self.__mid_23)
            self.__b['DN'] = self.__get_b_of_line(self.__point_3)
            self.__b['UP'] = self.__get_b_of_line(self.__point_2)
            self.__b['DNM'] = self.__get_b_of_line(self.__m2)
            self.__b['UPM'] = self.__get_b_of_line(self.__m1)
            self.__b['MID'] = self.__get_b_of_line(self.__mid_23)

    def __get_b_of_line(self, coordinate):
        return coordinate['y'] - get_in_milliseconds(coordinate['x']) * self.__M

    def get_all(self):
        return {'mid_23': self.__mid_23, 'mid_12': self.__mid_12, 'M': self.__M, 'm1': self.__m1, 'm2': self.__m2,
                'b': self.__b, 'convention': self.__convention, 'point_1': self.__point_1, 'point_2': self.__point_2,
                'point_3': self.__point_3}

    def check_price_state(self, x, y):
        if (self.__M * get_in_milliseconds(x) + self.__b['UP']) <= y:
            return 0
        if (self.__M * get_in_milliseconds(x) + self.__b['UPM']) <= y:
            return 1
        if (self.__M * get_in_milliseconds(x) + self.__b['MID']) <= y:
            return 2
        if (self.__M * get_in_milliseconds(x) + self.__b['DNM']) <= y:
            return 3
        if (self.__M * get_in_milliseconds(x) + self.__b['DN']) <= y:
            return 4
        return 5

    def get_y_for_all_lines(self, x):
        x = get_in_milliseconds(x)
        return {'UP': self.__M * x + self.__b['UP'],
                'UPM': self.__M * x + self.__b['UPM'],
                'MID': self.__M * x + self.__b['MID'],
                'DNM': self.__M * x + self.__b['DNM'],
                'DN': self.__M * x + self.__b['DN']}

    def get_plot(self, mid_val_points, revision_points, p=None,show_graph=False):
        graph_model = VisualAnalysis()
        all_points = self.get_all()
        all_points['GRAD_UP'] = {'y': self.get_y_for_all_lines(Constants.EVAL_TIMESTAMP)['UP'],
                                 'x': np.datetime64(Constants.EVAL_TIMESTAMP)}
        all_points['GRAD_DN'] = {'y': self.get_y_for_all_lines(Constants.EVAL_TIMESTAMP)['DN'],
                                 'x': np.datetime64(Constants.EVAL_TIMESTAMP)}
        all_points['GRAD_DNM'] = {'y': self.get_y_for_all_lines(Constants.EVAL_TIMESTAMP)['DNM'],
                                  'x': np.datetime64(Constants.EVAL_TIMESTAMP)}
        all_points['GRAD_UPM'] = {'y': self.get_y_for_all_lines(Constants.EVAL_TIMESTAMP)['UPM'],
                                  'x': np.datetime64(Constants.EVAL_TIMESTAMP)}
        all_points['GRAD_MID'] = {'y': self.get_y_for_all_lines(Constants.EVAL_TIMESTAMP)['MID'],
                                  'x': np.datetime64(Constants.EVAL_TIMESTAMP)}
        if len(mid_val_points) > 0:
            all_points['MID'] = mid_val_points
        else:
            all_points['MID'] = []

        if len(revision_points) > 0:
            all_points['REV'] = revision_points
        else:
            all_points['REV'] = []

        p = graph_model.get_slope_for_pitch_fork(self.__M, self.__b, all_points , p)  # slope

        if show_graph:
            show(p)

        logger.add('INFO', 'The Pitchfork graph is created.')

        return p


def analysis_pitchfork(pitch_fork_model, mid_validation_data, revision_validation_data):
    # Median validation count
    mid_validation_data.reset_index(drop=True, inplace=True)
    mid_cuts = 0
    mid_validation_points = []
    if mid_validation_data.shape[0] > 1:
        for index in range(mid_validation_data.shape[0] - 1, 0, -1):
            y_next = mid_validation_data.close[index]
            x_next = mid_validation_data.time[index]
            y = mid_validation_data.close[index - 1]
            x = mid_validation_data.time[index - 1]
            sts_xy = pitch_fork_model.check_price_state(x, y)
            sts_xy_next = pitch_fork_model.check_price_state(x_next, y_next)
            if 2 < sts_xy and 2 >= sts_xy_next:
                mid_validation_points.append({'x': np.datetime64(x), 'y': y})
                mid_cuts += 1  # Minima to maxima
            elif 2 > sts_xy and 2 <= sts_xy_next:
                mid_cuts += 1  # Maxima to minima

    # Revision validation count
    revision_count = 0
    revision_points = []
    for index in range(revision_validation_data.shape[0] - 1):
        if revision_validation_data.close[index] < revision_validation_data.close[index + 1]:
            y_down_line = pitch_fork_model.get_y_for_all_lines(revision_validation_data.time.values[index])['DN']
            if abs(y_down_line - revision_validation_data.close[index]) <= (Constants.REVISION_THRESHOLD * y_down_line):
                if pitch_fork_model.check_price_state(revision_validation_data.time[index],
                                                      revision_validation_data.close[index]) >= 4:
                    revision_count += 1
                    revision_points.append({'y': revision_validation_data.close[index],
                                            'x': np.datetime64(revision_validation_data.time[index])})

    return mid_cuts, revision_count, mid_validation_points, revision_points


def transcend_pitchfork(data):
    try:
        day_of_test = np.datetime64('today') - pd.Timedelta(Constants.MONTH_OF_TEST, unit='M')
        day_of_analysis = np.datetime64('today') - pd.Timedelta(Constants.MONTH_OF_ANALYSIS + Constants.MONTH_OF_TEST,
                                                                unit='M')
        analysis_data = get_max_min_points(
            data[(data['time'] < day_of_test) & (data['time'] > day_of_analysis)], 'close').reset_index(drop=True)
        analysis_data_time = analysis_data['time'].values
        analysis_data_close = analysis_data['close'].values
    except KeyError:
        logger.add("ERROR", "Not enough data, running out of index")
        return None
    max_touches = 0
    revise_touches = 0
    optimum_pitchfork = None
    op_plot = None
    for p2 in range(1, analysis_data.shape[0] - 1):
        for p3 in range(p2):
            revise_data = get_max_min_points(data[data['time'] > np.datetime64(analysis_data_time[p3])], 'close')
            revise_data.reset_index(inplace=True, drop=True)
            for p1 in range(p2 + 1, analysis_data.shape[0]):
                point_x = [np.datetime64(analysis_data_time[p1]),
                           np.datetime64(analysis_data_time[p2]),
                           np.datetime64(analysis_data_time[p3])]
                point_y = [analysis_data_close[p1], analysis_data_close[p2], analysis_data_close[p3]]
                pitch_fork_model = PitchFork(point_x, point_y, mode='ModSchiff')
                if not pitch_fork_model.get_all()['convention']:
                    continue

                mid_touches, revision_counter, mid_val_points, revision_points = \
                    analysis_pitchfork(pitch_fork_model, analysis_data[p2: p1], revise_data)
                if (mid_touches + revision_counter) > (max_touches + revise_touches) and revision_counter != 0:
                    if mid_touches > 4:
                        continue
                    max_touches = mid_touches
                    revise_touches = revision_counter
                    optimum_pitchfork = pitch_fork_model
                    op_plot = optimum_pitchfork.get_plot(mid_val_points, revision_points)
                    logger.add("INFO", 'Pitchfork points are updated. MID_VALIDATION: {}. REVISION_VALIDATION: {}'.
                               format(max_touches, revise_touches))
    return optimum_pitchfork, op_plot


# if __name__ == '__main__':
#     A = FetchHistFromES('D', 365)
#     B = A.get_stock_data("TITAN", False)
#     C, ploty = transcend_pitchfork(B)
#     show(ploty)
#     print(C.get_all())
    # max_min_points = get_max_min_points(B, 'close')
    # p_x = max_min_points['time'].values
    # p_y = max_min_points['close'].values
    # model = PitchFork([p_x[0], p_x[4], p_x[7]], [p_y[0], p_y[4], p_y[7]])
    # details = model.get_all()
    # print(details)
    # print(model.get_y_for_all_lines(point_x[-1:][0]))
    # model.get_plot(show_graph=True)
