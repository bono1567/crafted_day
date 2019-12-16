import os
from functools import lru_cache
from os.path import dirname, join

import pandas as pd

from bokeh.io import curdoc
from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource, PreText, Select
from bokeh.plotting import figure

def CreateFigure(name, data):
    entity_names = data.columns[1:].values.tolist()
    p = figure(title=name, plot_width=200, plot_height=200)
    p.line

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
    for stock, file in zip(stocks_data,file_names):
        figures.append(CreateFigure(file, stock))