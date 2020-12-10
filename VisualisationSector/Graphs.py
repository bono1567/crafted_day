import pandas as pd
from bokeh.plotting import figure, ColumnDataSource
from bokeh.io import curdoc, show, output_file
from bokeh.layouts import column
from bokeh.models.widgets import Tabs, Panel
from bokeh.models import BooleanFilter, CDSView, HoverTool, DatetimeTickFormatter, Slope
from bokeh.palettes import Category20
from bokeh.models.formatters import NumeralTickFormatter
from Harvester.Utils import get_max_min_points
from LoggerApi.Logger import Logger


def get_point_data(data_points):
    x = []
    y = []
    for item in data_points:
        x.append(item['x'])
        y.append(item['y'])
    return x, y


class VisualAnalysis(Logger):
    __W_PLOT = 1000
    __H_PLOT = 400
    __TOOLS = 'pan,wheel_zoom,reset,save,box_select,box_zoom'

    __VBAR_WIDTH = 12 * 60 * 60 * 1000
    __RED = Category20[7][6]
    __GREEN = Category20[5][4]
    __BLUE = Category20[3][0]
    __GRAY = Category20[12][11]

    d_formatter = DatetimeTickFormatter(
        hours=["%d %B %Y"],
        days=["%d %B %Y"],
        months=["%d %B %Y"],
        years=["%d %B %Y"],
    )

    def __init__(self, width=1500, height=600, tools=None, bar_width=0):
        super().__init__(VisualAnalysis.__name__, 'VIZ_LOG')
        self.__W_PLOT = width
        self.__H_PLOT = height
        if bar_width != 0:
            self.__VBAR_WIDTH = bar_width
        if tools is not None:
            self.__TOOLS = tools

    def __to_col_data_source(self, data):
        stock_data = ColumnDataSource(data=dict(date=[], open=[], close=[], high=[], low=[], MFI=[], MACD_Hist=[],
                                                MACD=[], MACD_Signal=[], ADX=[], index=[]))
        data['date'] = pd.to_datetime(data['time'], format='%Y-%m-%d')
        stock_data.data = stock_data.from_df(data)
        try:
            self.add("INFO", "ColumnDataSource created for {}".format(data['symbol'].values[0]))
        except KeyError:
            self.add("INFO", "For the min_max pointers.")
        return stock_data

    "Candle stick representation of the stock."

    def get_candlestick(self, data, show_graph=True, p=None):
        stock_data = self.__to_col_data_source(data)
        title = "{} Data ({}, Code:{})".format(stock_data.data['security_name'][0],
                                               stock_data.data['symbol'][0], stock_data.data['code'][0])
        if p is None:
            p = figure(x_axis_type="datetime", plot_width=self.__W_PLOT, plot_height=self.__H_PLOT, tools=self.__TOOLS
                       , title=title, toolbar_location='above')

        inc = stock_data.data['close'] > stock_data.data['open']
        dec = stock_data.data['open'] > stock_data.data['close']
        view_inc = CDSView(source=stock_data, filters=[BooleanFilter(inc)])
        view_dec = CDSView(source=stock_data, filters=[BooleanFilter(dec)])

        self.__set_xy_settings(p)

        p.segment(x0='date', x1='date', y0='low', y1='high', color=self.__GREEN, source=stock_data, view=view_inc)
        p.segment(x0='date', x1='date', y0='low', y1='high', color=self.__RED, source=stock_data, view=view_dec)

        main_vbar_green = p.vbar(x='date', width=self.__VBAR_WIDTH, top='open', bottom='close', fill_color=self.__GREEN,
                                 line_color=self.__GREEN, source=stock_data, view=view_inc, name="price")
        main_vbar_red = p.vbar(x='date', width=self.__VBAR_WIDTH, top='open', bottom='close', fill_color=self.__RED,
                               line_color=self.__RED, source=stock_data, view=view_dec, name="price")

        hover_tool = HoverTool(tooltips=[
            ("Date", "@time{%d-%b-%y}"),
            ("Open", "@open{Rs.0,0.00}"),
            ("Close", "@close{Rs.0,0.00}"),
            ("Volume", "@volume{(0.00 a)}")
        ], renderers=[main_vbar_green, main_vbar_red], formatters={"@time": 'datetime'})
        p.tools.append(hover_tool)

        elements = list()
        elements.append(p)
        curdoc().add_root(column(elements))
        curdoc().title = stock_data.data['security_name'][0] + '_CS'
        if show_graph:
            output_file(stock_data.data['symbol'][0] + '_CS.html',
                        '{} {}'.format(stock_data.data['security_name'][0], stock_data.data['code'][0]))
            show(p)

        return p

    "Close price/ MFI/ ADX in line format"

    def get_trend_line(self, data, col_name, show_graph=True, p=None):
        stock_data = self.__to_col_data_source(data)
        max_min_data = self.__to_col_data_source(get_max_min_points(data, 'close'))
        title = "{} Data ({}, Code:{})".format(stock_data.data['security_name'][0],
                                               stock_data.data['symbol'][0], stock_data.data['code'][0])

        if p is None:
            p = figure(x_axis_type="datetime", plot_width=self.__W_PLOT, plot_height=self.__H_PLOT, tools=self.__TOOLS
                       , title=title, toolbar_location='above')

        if col_name == 'close':
            color = self.__BLUE
        elif col_name == 'MFI':
            color = self.__GRAY
        else:
            color = self.__GREEN
        main_line = p.line(x='date', y=col_name, source=stock_data, line_color=color, name=col_name)
        if col_name is 'close':
            p.circle_dot(x='date', y='close', source=max_min_data, line_color=self.__BLUE)

        self.__set_xy_settings(p)

        hover_tool = HoverTool(tooltips=[
            ("Date", "@time{%d-%b-%y}"),
            (col_name.upper(), "@" + col_name + "{0,0.00}"),
            ("Close", "@close{Rs.0,0.00}"),
            ("Volume", "@volume{(0.00 a)}")
        ], renderers=[main_line], formatters={"@time": 'datetime'})
        p.tools.append(hover_tool)

        elements = list()
        elements.append(p)
        curdoc().add_root(column(elements))
        curdoc().title = stock_data.data['security_name'][0] + '_' + col_name

        if show_graph:
            output_file(stock_data.data['symbol'][0] + '_{}.html'.format(col_name),
                        '{} {}'.format(stock_data.data['security_name'][0], stock_data.data['code'][0]))
            show(p)

        return p

    """MACD indicator plot."""

    def get_macd_plot(self, data, show_graph=False, p=None):
        stock_data = self.__to_col_data_source(data)

        title = "{} Data ({}, Code:{})".format(stock_data.data['security_name'][0],
                                               stock_data.data['symbol'][0], stock_data.data['code'][0])

        if p is None:
            p = figure(x_axis_type="datetime", plot_width=self.__W_PLOT, plot_height=self.__H_PLOT, tools=self.__TOOLS
                       , title=title, toolbar_location='above')

        macd_hist = p.vbar(x='date', width=self.__VBAR_WIDTH, top='MACD_Hist', fill_color=self.__GRAY,
                           line_color=self.__GRAY, source=stock_data, name="macd_hist")
        macd_line = p.line(x='date', y='MACD', source=stock_data, line_color=self.__BLUE, name="macd_line")
        macd_signal = p.line(x='date', y='MACD_Signal', source=stock_data, line_color=self.__RED, name="macd_signal")

        self.__set_xy_settings(p)

        hover_tool = HoverTool(tooltips=[
            ("Date", "@time{%d-%b-%y}"),
            ("MACD", "@MACD{(0, 0.00)}"),
            ("MACD_S", "@MACD_Signal{(0, 0.00)}"),
            ("MACD_Hist", "@MACD_Hist{(0, 0.00)}")
        ], renderers=[macd_hist, macd_line, macd_signal], formatters={"@time": 'datetime'})
        p.tools.append(hover_tool)

        elements = list()
        elements.append(p)
        curdoc().add_root(column(elements))
        curdoc().title = stock_data.data['security_name'][0] + 'MACD'

        if show_graph:
            output_file(stock_data.data['symbol'][0] + '_MACD.html',
                        '{} {}'.format(stock_data.data['security_name'][0], stock_data.data['code'][0]))
            show(p)

        return p

    "Volume traded histogram."

    def get_volume_hist(self, data, show_graph=False, p=None):
        stock_data = self.__to_col_data_source(data)
        title = "{} Data ({}, Code:{})".format(stock_data.data['security_name'][0],
                                               stock_data.data['symbol'][0], stock_data.data['code'][0])

        if p is None:
            p = figure(x_axis_type="datetime", plot_width=self.__W_PLOT, plot_height=self.__H_PLOT - 200,
                       tools=self.__TOOLS
                       , title=title, toolbar_location='above', y_range=(0, data['volume'].max()))

        main_vbar = p.vbar(x='date', width=self.__VBAR_WIDTH, top='volume', fill_color=self.__GRAY,
                           line_color=self.__GRAY, source=stock_data, name="volume")

        self.__set_xy_settings(p)

        hover_tool = HoverTool(tooltips=[
            ("Date", "@time{%d-%b-%y}"),
            ("Open", "@open{Rs.0,0.00}"),
            ("Close", "@close{Rs.0,0.00}"),
            ("Volume", "@volume{(0.00 a)}")
        ], renderers=[main_vbar], formatters={"@time": 'datetime'})
        p.tools.append(hover_tool)

        elements = list()
        elements.append(p)
        curdoc().add_root(column(elements))
        curdoc().title = stock_data.data['security_name'][0] + 'VOL'

        if show_graph:
            output_file(stock_data.data['symbol'][0] + '_VOL.html',
                        '{} {}'.format(stock_data.data['security_name'][0], stock_data.data['code'][0]))
            show(p)

        return p

    def __set_xy_settings(self, p):
        p.xaxis.formatter = self.d_formatter
        p.xaxis.major_label_orientation = 3.14 / 4
        p.grid.grid_line_alpha = 0.3

        p.yaxis.formatter = NumeralTickFormatter(format='0,0[.]000')
        p.x_range.range_padding = 0.05
        p.xaxis.ticker.desired_num_ticks = 40
        p.xaxis.major_label_orientation = 3.14 / 4

    def show_all(self, items, stock_name):
        panels = []
        if 'cd_stick' in items.keys():
            panels.append(Panel(child=column(items['cd_stick'], items['volume']), title='CandleStick/Volume'))
        if 'price' in items.keys():
            panels.append(Panel(child=column(items['price'], items['volume']), title='Price/Volume'))
        if 'MACD' in items.keys():
            panels.append(Panel(child=column(items['MACD'], items['cd_stick']), title='MACD'))
        if 'MFI' in items.keys():
            panels.append(Panel(child=column(items['MFI'], items['cd_stick']), title='MFI'))
        if 'ADX' in items.keys():
            panels.append(Panel(child=column(items['ADX'], items['cd_stick']), title='ADX'))
        if 'PITCH_FORK' in items.keys():
            panels.append(Panel(child=column(items['PITCH_FORK']), title="MOD. SCHIFF'S PITCHFORK"))
        tabs = Tabs(tabs=panels)
        elements = list()
        elements.append(tabs)
        curdoc().add_root(column(elements))
        curdoc().title = stock_name + '_TABS'
        output_file(stock_name + '_TABS.html')
        show(tabs)
        self.add("INFO", "TABS VIEW ON.")

    """Other util plots"""

    def get_line(self, point_a, point_b, p=None, colour='gray', show_graph=False):
        title = 'UTIL_PLOT'

        if p is None:
            p = figure(x_axis_type="datetime", plot_width=self.__W_PLOT, plot_height=self.__H_PLOT - 200,
                       tools=self.__TOOLS
                       , title=title, toolbar_location='above', y_range=(-abs(point_a['y'] + 0.2 * point_a['y']),
                                                                         abs(point_a['y'] + 0.2 * point_a['y'])))

        if colour is 'b':
            color = self.__BLUE
        elif colour is 'g':
            color = self.__GREEN
        elif colour is 'r':
            color = self.__RED
        else:
            color = self.__GRAY
        p.line([point_a['x'], point_b['x']], [point_a['y'], point_b['y']], line_width=4, color=color)
        p.circle([point_a['x'], point_b['x']], [point_a['y'], point_b['y']], size=10, color=color)
        self.__set_xy_settings(p)

        elements = list()
        elements.append(p)
        curdoc().add_root(column(elements))

        if show_graph:
            show(p)

        return p

    def get_slope_for_pitch_fork(self, m, b, plot_data, p=None, show_graph=False, layout=False, debug=False):
        if p is None:
            p = figure(x_axis_type="datetime", plot_width=self.__W_PLOT, plot_height=self.__W_PLOT - 800,
                       tools=self.__TOOLS, toolbar_location='above')

        point_data = {'MID': get_point_data(plot_data['MID']), 'REV': get_point_data(plot_data['REV'])}

        p = self.get_line(plot_data['point_1'], plot_data['point_2'], p=p, colour='b')
        p = self.get_line(plot_data['point_2'], plot_data['point_3'], p=p, colour='b')
        p = self.get_line(plot_data['mid_23'], plot_data['mid_12'], p=p)
        p = self.get_line(plot_data['point_2'], plot_data['GRAD_UP'], p=p)  # UP
        p = self.get_line(plot_data['point_3'], plot_data['GRAD_DN'], p=p)  # DN
        p = self.get_line(plot_data['mid_23'], plot_data['GRAD_MID'], p=p, colour='b')  # MID
        p = self.get_line(plot_data['m1'], plot_data['GRAD_UPM'], p=p, colour='g')  # UPM
        p = self.get_line(plot_data['m2'], plot_data['GRAD_DNM'], p=p, colour='r')  # DNM

        if debug:
            p.circle(x=point_data['MID'][0], y=point_data['MID'][1], size=10, color=self.__GRAY)
            p.circle(x=point_data['REV'][0], y=point_data['REV'][1], size=10, color=self.__RED)

        if layout:
            p.add_layout(Slope(gradient=m, y_intercept=b['UP'], line_color=self.__GRAY))
            p.add_layout(Slope(gradient=m, y_intercept=b['UPM'], line_color=self.__GREEN))
            p.add_layout(Slope(gradient=m, y_intercept=b['MID'], line_color=self.__BLUE))
            p.add_layout(Slope(gradient=m, y_intercept=b['DNM'], line_color=self.__RED))
            p.add_layout(Slope(gradient=m, y_intercept=b['DN'], line_color=self.__GRAY))

        self.__set_xy_settings(p)

        elements = list()
        elements.append(p)
        curdoc().add_root(column(elements))

        if show_graph:
            show(p)

        return p
