import pandas as pd
from bokeh.plotting import figure, ColumnDataSource
from bokeh.io import curdoc, show, output_file
from bokeh.layouts import row, column
from bokeh.models.widgets import Tabs, Panel
from bokeh.models import BooleanFilter, CDSView, HoverTool, DatetimeTickFormatter
from bokeh.palettes import Category20
from bokeh.models.formatters import NumeralTickFormatter
from Models.Utils.CalculationUtils import get_max_min_points
from LoggerApi.Logger import Logger


class VisualAnalysis(Logger):
    __W_PLOT = 1500
    __H_PLOT = 400
    __TOOLS = 'pan,wheel_zoom,hover,reset,save'

    __VBAR_WIDTH = 12 * 60 * 60 * 1000
    __RED = Category20[7][6]
    __GREEN = Category20[5][4]
    __BLUE = Category20[3][0]
    __GRAY = Category20[12][11]

    def __init__(self, width=1500, height=600, __tools='', bar_width=0):
        super().__init__(VisualAnalysis.__name__, 'VIZ_LOG')
        self.__W_PLOT = width
        self.__H_PLOT = height
        if __tools != '':
            self.__TOOLS = __tools
        if bar_width != 0:
            self.__VBAR_WIDTH = bar_width

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

    def get_candlestick(self, data, show_graph=True, p=None):
        stock_data = self.__to_col_data_source(data)
        title = "{} Data ({}, Code:{})".format(stock_data.data['security_name'][0],
                                               stock_data.data['symbol'][0], stock_data.data['code'][0])
        if p is None:
            p = figure(x_axis_type="datetime", plot_width=self.__W_PLOT, plot_height=self.__H_PLOT, __tools=self.__TOOLS
                       , title=title, toolbar_location='above')

        inc = stock_data.data['close'] > stock_data.data['open']
        dec = stock_data.data['open'] > stock_data.data['close']
        view_inc = CDSView(source=stock_data, filters=[BooleanFilter(inc)])
        view_dec = CDSView(source=stock_data, filters=[BooleanFilter(dec)])

        p.xaxis.formatter = DatetimeTickFormatter(
            hours=["%d %B %Y"],
            days=["%d %B %Y"],
            months=["%d %B %Y"],
            years=["%d %B %Y"],
        )
        p.xaxis.major_label_orientation = 3.14 / 4
        p.grid.grid_line_alpha = 0.3

        p.segment(x0='date', x1='date', y0='low', y1='high', color=self.__GREEN, source=stock_data, view=view_inc)
        p.segment(x0='date', x1='date', y0='low', y1='high', color=self.__RED, source=stock_data, view=view_dec)

        p.vbar(x='date', width=self.__VBAR_WIDTH, top='open', bottom='close', fill_color=self.__GREEN,
               line_color=self.__GREEN, source=stock_data, view=view_inc, name="price")
        p.vbar(x='date', width=self.__VBAR_WIDTH, top='open', bottom='close', fill_color=self.__RED,
               line_color=self.__RED, source=stock_data, view=view_dec, name="price")

        p.yaxis.formatter = NumeralTickFormatter(format='Rs. 0,0[.]000')
        p.x_range.range_padding = 0.05
        p.xaxis.ticker.desired_num_ticks = 40
        p.xaxis.major_label_orientation = 3.14 / 4

        price_hover = p.select(dict(type=HoverTool))

        price_hover.names = ["price"]
        # Creating tooltips
        price_hover.tooltips = [("Date", "@time{%d-%b-%y}"),
                                ("Open", "@open{Rs.0,0.00}"),
                                ("Close", "@close{Rs.0,0.00}"),
                                ("Volume", "@volume{(0.00 a)}")]
        price_hover.formatters = {"@time": 'datetime'}

        # elements = list()
        # elements.append(p)
        # curdoc().add_root(column(elements))
        # curdoc().title = stock_data.data['security_name'][0]
        if show_graph:
            output_file(stock_data.data['symbol'][0] + '_CS.html',
                        '{} {}'.format(stock_data.data['security_name'][0], stock_data.data['code'][0]))
            show(p)

        return p

    def get_trend_line(self, data, show_graph=True, p=None):
        stock_data = self.__to_col_data_source(data)
        max_min_data = self.__to_col_data_source(get_max_min_points(data, 'close'))
        title = "{} Data ({}, Code:{})".format(stock_data.data['security_name'][0],
                                               stock_data.data['symbol'][0], stock_data.data['code'][0])

        if p is None:
            p = figure(x_axis_type="datetime", plot_width=self.__W_PLOT, plot_height=self.__H_PLOT, __tools=self.__TOOLS
                       , title=title, toolbar_location='above')

        p.xaxis.formatter = DatetimeTickFormatter(
            hours=["%d %B %Y"],
            days=["%d %B %Y"],
            months=["%d %B %Y"],
            years=["%d %B %Y"],
        )
        p.xaxis.major_label_orientation = 3.14 / 4
        p.grid.grid_line_alpha = 0.3

        p.line(x='date', y='close', source=stock_data, line_color=self.__BLUE, name="price")
        p.circle_dot(x='date', y='close', source=max_min_data, line_color=self.__BLUE)

        price_hover = p.select(dict(type=HoverTool))

        price_hover.names = ["price"]
        # Creating tooltips
        price_hover.tooltips = [("Date", "@time{%d-%b-%y}"),
                                ("Open", "@open{Rs.0,0.00}"),
                                ("Close", "@close{Rs.0,0.00}"),
                                ("Volume", "@volume{(0.00 a)}")]
        price_hover.formatters = {"@time": 'datetime'}

        # elements = list()
        # elements.append(p)
        # curdoc().add_root(column(elements))
        # curdoc().title = stock_data.data['security_name'][0]

        if show_graph:
            output_file(stock_data.data['symbol'][0] + '_PR.html',
                        '{} {}'.format(stock_data.data['security_name'][0], stock_data.data['code'][0]))
            show(p)

        return p

    def get_volume_hist(self, data, show_graph=False, p=None):
        stock_data = self.__to_col_data_source(data)
        title = "{} Data ({}, Code:{})".format(stock_data.data['security_name'][0],
                                               stock_data.data['symbol'][0], stock_data.data['code'][0])

        if p is None:
            p = figure(x_axis_type="datetime", plot_width=self.__W_PLOT, plot_height=self.__H_PLOT-200, __tools=self.__TOOLS
                       , title=title, toolbar_location='above', y_range=(0, data['volume'].max()))

        p.vbar(x='date', width=self.__VBAR_WIDTH, top='volume', fill_color=self.__GRAY,
               source=stock_data, name="volume")

        price_hover = p.select(dict(type=HoverTool))
        price_hover.names = ["volume"]
        # Creating tooltips
        price_hover.tooltips = [("Date", "@time{%d-%b-%y}"),
                                ("Open", "@open{Rs.0,0.00}"),
                                ("Close", "@close{Rs.0,0.00}"),
                                ("Volume", "@volume{(0.00 a)}")]
        price_hover.formatters = {"@time": 'datetime'}

        # elements = list()
        # elements.append(p)
        # curdoc().add_root(column(elements))
        # curdoc().title = stock_data.data['security_name'][0]

        if show_graph:
            output_file(stock_data.data['symbol'][0] + '_VOL.html',
                        '{} {}'.format(stock_data.data['security_name'][0], stock_data.data['code'][0]))
            show(p)

        return p

    def show_all(self, items, stock_name):
        panels = []
        if 'cd_stick' in items.keys():
            panels.append(Panel(child=column(items['cd_stick'], items['volume']), title='CandleStick/Volume'))
        if 'price' in items.keys():
            panels.append(Panel(child=column(items['price'], items['volume']), title='Price/Volume'))
        if 'MACD' in items.keys():
            panels.append(Panel(child=column(items['MACD']), title='MACD'))
        if 'MFI' in items.keys():
            panels.append(Panel(child=column(items['MFI']), title='MFI'))
        if 'ADX' in items.keys():
            panels.append(Panel(child=column(items['ADX']), title='ADX'))
        tabs = Tabs(tabs=panels)
        elements = list()
        elements.append(tabs)
        curdoc().add_root(column(elements))
        curdoc().title = stock_name
        output_file(stock_name + '_TABS.html')
        show(tabs)
        self.add("INFO", "TABS VIEW ON.")






