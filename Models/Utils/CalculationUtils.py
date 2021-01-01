"""Model analysis utils."""
import datetime
import glob
import pathlib

from bokeh.io import show
import pandas as pd
import numpy as np

import Constants
from Harvester.Utils import get_max_min_points
from LoggerApi.Logger import Logger
from VisualisationSector.Graphs import VisualAnalysis

LOGGER = Logger(__file__, 'CALCULATION_LOG')
BASE_PATH = pathlib.Path(__file__).parent.parent.parent


class RiskRewardForStock:
    """The RR calculator util."""
    ratio = 0

    def get_ratio(self, amount_invested, expected_book_price, stop_loss_amount):
        """:return ratio float."""
        if amount_invested > expected_book_price:
            LOGGER.add("ERROR", "You are expecting a loss from your investment")
            return None
        if stop_loss_amount > amount_invested:
            LOGGER.add("ERROR", "Your stop loss amount is greater than the amount invested.")
            return None
        self.ratio = (expected_book_price - amount_invested) / (amount_invested - stop_loss_amount)
        return self.ratio

    def get_rating(self, amount_invested, expected_book_price, stop_loss_amount):
        """:return String for each ratio status."""
        if self.ratio == 0:
            self.get_ratio(amount_invested, expected_book_price, stop_loss_amount)
        if self.ratio > 4.0:
            return Constants.HL
        if self.ratio > 3.0:
            return Constants.AL
        if self.ratio > 2.0:
            return Constants.AA
        return Constants.LH


def get_date_midpoint(date_1, date_2):
    """:return date mid-point (Date format)."""
    return date_1 + (date_2 - date_1) / 2


def get_mid_point(coordinate_1, coordinate_2):
    """Gives the midpoint for the graph implementation and analysis."""
    return {'y': (coordinate_1['y'] + coordinate_2['y']) / 2,
            'x': get_date_midpoint(coordinate_1['x'], coordinate_2['x'])}


def get_slope(mid_12, mid_23):
    """Slope between two points."""
    denominator = (mid_23['x'] - mid_12['x']).astype('int64') * 1e-6
    return (mid_23['y'] - mid_12['y']) / denominator


def get_in_milliseconds(for_date):
    """Convert time to milliseconds for implementation in graphs"""
    ns_date = np.datetime64(for_date, 'ns').astype('int64')
    return ns_date * 1e-6


class PitchFork:
    """
    Implemented the Modified Schiff's pitchfork.
    """
    __b = {}

    def __init__(self, points_x, points_y, mode='ModSchiff'):
        self.__point_1 = {'x': points_x[0], 'y': points_y[0]}
        self.__point_2 = {'x': points_x[1], 'y': points_y[1]}
        self.__point_3 = {'x': points_x[2], 'y': points_y[2]}
        if mode == 'ModSchiff':
            self.__mid_12 = get_mid_point(self.__point_1, self.__point_2)
            self.__mid_23 = get_mid_point(self.__point_2, self.__point_3)

            if not self.__get_convention():
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

    def __get_convention(self):
        return (self.__point_2['y'] > self.__point_3['y']
                ) and (self.__point_2['y'] > self.__point_1['y'])

    def __get_b_of_line(self, coordinate):
        """:return the y-intercept."""
        return coordinate['y'] - get_in_milliseconds(
            coordinate['x']) * get_slope(self.__mid_12, self.__mid_23)

    def get_all(self):
        """Returns all the variables of the class."""
        return {'mid_23': self.__mid_23, 'mid_12': self.__mid_12,
                'M': get_slope(self.__mid_12, self.__mid_23), 'm1': self.__m1, 'm2': self.__m2,
                'b': self.__b, 'convention': self.__get_convention(),
                'point_1': self.__point_1, 'point_2': self.__point_2,
                'point_3': self.__point_3}

    def check_price_state(self, x_of_point, y_of_point):
        """Gives the status of the point with respect to pitch-fork lines."""
        if (get_slope(self.__mid_12, self.__mid_23
                      ) * get_in_milliseconds(x_of_point) + self.__b['UP']) <= y_of_point:
            return 0
        if (get_slope(self.__mid_12, self.__mid_23
                      ) * get_in_milliseconds(x_of_point) + self.__b['UPM']) <= y_of_point:
            return 1
        if (get_slope(self.__mid_12, self.__mid_23
                      ) * get_in_milliseconds(x_of_point) + self.__b['MID']) <= y_of_point:
            return 2
        if (get_slope(self.__mid_12, self.__mid_23
                      ) * get_in_milliseconds(x_of_point) + self.__b['DNM']) <= y_of_point:
            return 3
        if (get_slope(self.__mid_12, self.__mid_23
                      ) * get_in_milliseconds(x_of_point) + self.__b['DN']) <= y_of_point:
            return 4
        return 5

    def get_y_for_all_lines(self, x_of_point):
        """Gets the price for a particular date in all the pitchfork lines."""
        x_of_point = get_in_milliseconds(x_of_point)
        return {'UP': get_slope(self.__mid_12, self.__mid_23) * x_of_point + self.__b['UP'],
                'UPM': get_slope(self.__mid_12, self.__mid_23) * x_of_point + self.__b['UPM'],
                'MID': get_slope(self.__mid_12, self.__mid_23) * x_of_point + self.__b['MID'],
                'DNM': get_slope(self.__mid_12, self.__mid_23) * x_of_point + self.__b['DNM'],
                'DN': get_slope(self.__mid_12, self.__mid_23) * x_of_point + self.__b['DN']}

    def get_plot(self, mid_val_points, revision_points, plot=None, show_graph=False):
        """Returns the plot for the pitchfork model. Mainly for DEBUGGING."""
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
        if mid_val_points:
            all_points['MID'] = mid_val_points
        else:
            all_points['MID'] = []

        if revision_points:
            all_points['REV'] = revision_points
        else:
            all_points['REV'] = []

        plot = graph_model.get_slope_for_pitch_fork(
            get_slope(self.__mid_12, self.__mid_23), self.__b, all_points, plot)

        if show_graph:
            show(plot)

        LOGGER.add('INFO', 'The Pitchfork graph is created.')

        return plot


def analysis_pitchfork(pitch_fork_model, mid_validation_data, revision_validation_data):
    """The pitchfork analysis method."""
    # Median validation count
    mid_validation_data.reset_index(drop=True, inplace=True)
    mid_cuts = 0
    mid_validation_points = []
    if mid_validation_data.shape[0] > 1:
        for index in range(mid_validation_data.shape[0] - 1, 0, -1):
            y_next = mid_validation_data.close[index]
            x_next = mid_validation_data.time[index]
            y_current = mid_validation_data.close[index - 1]
            x_current = mid_validation_data.time[index - 1]
            sts_xy = pitch_fork_model.check_price_state(x_current, y_current)
            sts_xy_next = pitch_fork_model.check_price_state(x_next, y_next)
            if sts_xy > 2 >= sts_xy_next:
                mid_validation_points.append({'x': np.datetime64(x_current), 'y': y_current})
                mid_cuts += 1  # Minima to maxima
            elif sts_xy < 2 <= sts_xy_next:
                mid_cuts += 1  # Maxima to minima

    # Revision validation count
    revision_count = 0
    revision_points = []
    for index in range(revision_validation_data.shape[0] - 1):
        if revision_validation_data.close[index] < revision_validation_data.close[index + 1]:
            y_down_line = pitch_fork_model.get_y_for_all_lines(
                revision_validation_data.time.values[index])['DN']
            if abs(y_down_line - revision_validation_data.close[index]) \
                    <= (Constants.REVISION_THRESHOLD * y_down_line):
                if pitch_fork_model.check_price_state(revision_validation_data.time[index],
                                                      revision_validation_data.close[index]) >= 4:
                    revision_count += 1
                    revision_points.append({'y': revision_validation_data.close[index],
                                            'x': np.datetime64(
                                                revision_validation_data.time[index])})

    return mid_cuts, revision_count, mid_validation_points, revision_points


def transcend_pitchfork(data):
    """The model for selecting best pitchfork points."""
    try:
        analysis_data = get_max_min_points(
            data[(data['time'] < np.datetime64('today') -
                  pd.Timedelta(Constants.MONTH_OF_TEST, unit='M'))
                 & (data['time'] > np.datetime64('today') -
                    pd.Timedelta(Constants.MONTH_OF_ANALYSIS + Constants.MONTH_OF_TEST, unit='M'))],
            'close').reset_index(drop=True)
        analysis_data_time = analysis_data['time'].values
        analysis_data_close = analysis_data['close'].values
    except KeyError:
        LOGGER.add("ERROR", "Not enough data, running out of index")
        return None
    max_touches = 0
    revise_touches = 0
    op_points = []
    op_plot = None
    for p_2 in range(1, analysis_data.shape[0] - 1):
        for p_3 in range(p_2):
            revise_data = get_max_min_points(
                data[data['time'] > np.datetime64(analysis_data_time[p_3])], 'close')
            revise_data.reset_index(inplace=True, drop=True)
            for p_1 in range(p_2 + 1, analysis_data.shape[0]):

                pitch_fork_model = PitchFork([np.datetime64(analysis_data_time[p_1]),
                                              np.datetime64(analysis_data_time[p_2]),
                                              np.datetime64(analysis_data_time[p_3])],
                                             [analysis_data_close[p_1],
                                              analysis_data_close[p_2],
                                              analysis_data_close[p_3]], mode='ModSchiff')

                if not pitch_fork_model.get_all()['convention']:
                    continue

                return_goods = analysis_pitchfork(pitch_fork_model,
                                                  analysis_data[p_2: p_1],
                                                  revise_data)
                if (return_goods[0] + return_goods[1]) > (
                        max_touches + revise_touches) and return_goods[1] != 0:
                    if return_goods[0] > 4:
                        continue
                    max_touches = return_goods[0]
                    revise_touches = return_goods[1]
                    op_points = [p_1, p_2, p_3]
                    op_plot = pitch_fork_model.get_plot(return_goods[2], return_goods[3])
                    LOGGER.add("INFO", 'Pitchfork points are updated. MID_VALIDATION: {}.'
                                       ' REVISION_VALIDATION: {}'.
                               format(max_touches, revise_touches))
    optimum_pitchfork = PitchFork([np.datetime64(analysis_data_time[op_points[0]]),
                                   np.datetime64(analysis_data_time[op_points[1]]),
                                   np.datetime64(analysis_data_time[op_points[2]])],
                                  [analysis_data_close[op_points[0]],
                                   analysis_data_close[op_points[1]],
                                   analysis_data_close[op_points[2]]],
                                  mode='ModSchiff')
    return optimum_pitchfork, op_plot


def get_trend_of_stock(annual_data):
    """:return String signifying UP, DOWN or STAGNANT."""
    max_min_data = get_max_min_points(annual_data, 'adjusted_close')
    price = max_min_data['adjusted_close'].values
    size_of_data = len(price)
    up_count, down_count, prev_value = (0, 0, price[size_of_data - 1])
    for index in range(size_of_data - 3, 2, -2):
        if prev_value < price[index]:
            if price[index] < price[size_of_data - 1]:
                up_count = 0
            else:
                up_count += 1
        else:
            down_count += 1

    if price[0] > price[size_of_data - 1]:
        if up_count > 2 > down_count:
            return Constants.UP_SG
        if down_count > up_count:
            return Constants.UP_WK
        else:
            return Constants.UP
    elif price[0] < price[size_of_data - 1]:
        if down_count > 2 > up_count:
            return Constants.DN_SG
        if down_count < up_count:
            return Constants.DN_WK
        else:
            return Constants.DOWN
    else:
        return Constants.STAGNANT


def get_momentum_from_macd(stock_data):
    """It decides on the momentum of the market. """
    macd = stock_data['MACD_Hist']
    slope = "PULLING_TO_BULL"
    if macd[0] >= 0:
        for index, value in enumerate(macd):
            if index < 2:
                continue
            if value < macd[index - 1] > macd[index - 2]:
                slope = "PULLING_TO_BEAR"
                return slope, Constants.BULL
            if value < 0:
                return slope, Constants.BULL
    else:
        slope = "PULLING_TO_BEAR"
        for index, value in enumerate(macd):
            if index < 2:
                continue
            if value > macd[index - 1] < macd[index - 2]:
                slope = "PULLING_TO_BULL"
                return slope, Constants.BEAR
            if value > 0:
                return slope, Constants.BEAR


def get_dow_check_correlation(annual_data=None):
    """Check the correlation of the stock with the NIFTY50."""
    if annual_data is None:
        return None
    file_path = glob.glob(str(BASE_PATH) + "/Harvester/resources/NIFTY*")
    get_nifty = pd.read_csv(file_path[0])
    get_nifty = get_nifty[['Date', 'Close']]
    timestamp = [datetime.datetime.strptime(date, '%d-%b-%Y').strftime('%Y-%m-%d')
                 for date in get_nifty['Date'].values]
    get_nifty['time'] = pd.to_datetime(timestamp)
    get_nifty.drop('Date', axis=1)
    get_nifty = pd.merge(get_nifty, annual_data, on='time', how='inner')
    return get_nifty['Close'].corr(get_nifty['adjusted_close'])
