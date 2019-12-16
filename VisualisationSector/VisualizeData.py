import os
import pandas as pd
from bokeh.io import curdoc, show
from bokeh.layouts import column, row
from bokeh.models import Tabs, Panel
from bokeh.plotting import figure


def CreateFigure(name, data):
    entity_names = data.columns[1:].values.tolist()
    tabs = []
    price_stab = (data['close']-min(data['close']))/(max(data['close'])-min(data['close']))
    for col in entity_names:
        if col in ['time', 'open', 'high', 'low', 'close', 'dividend_amount', 'split_coefficient', 'adjusted_close']:
            continue
        y = (data[col]-min(data[col]))/(max(data[col])-min(data[col]))
        p = figure(title=name[:-4], plot_width=1400, plot_height=500, x_axis_type='datetime')
        p.line(data['time'], y, color='navy')
        p.line(data['time'], price_stab, color='red')
        tabs.append(Panel(child=p, title=col))

    return Tabs(tabs=tabs)


if __name__ == '__main__':

    ROOT_DIR = os.path.dirname(os.path.dirname(__file__))
    resource_path = os.path.join(ROOT_DIR, 'Harvester/resources')

    file_names = []
    for _, _, file in os.walk(resource_path):
        file_names = file

    stocks_data = []
    for stock in file_names:
        stocks_data.append(pd.read_csv(os.path.join(resource_path, stock), parse_dates=['time']))

    figures = []
    for stock, file in zip(stocks_data, file_names):
        figures.append(CreateFigure(file, stock))

    for fig in figures:
        show(fig)