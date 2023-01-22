"""Project view for crafted day."""
import glob
import json
from datetime import datetime
from html import escape

import aiohttp_jinja2
from aiohttp import web

from Harvester.HeadlineHarvester.DataArrangement import FTArrangeWithWords
from Harvester.StockPriceHarvester.DataArrangement import FetchHistFromES
from Harvester.StockPriceHarvester.NSEToolsHarvester.StockFromExistingData import FetchAllData
from LoggerApi.Logger import Logger
from Models.HistoricalModel import TechModel
from ServiceProvider.settings import BASE_DIR
from ServiceProvider.utils import get_nifty_history

LOGGER = Logger(filename=__file__, log_name='REQUEST_LOGS')


@aiohttp_jinja2.template('default.html')
async def index(request):
    """Index view for the web-app."""
    try:
        LOGGER.add('INFO', 'Default template returned. ID: {}'.format(request.headers['Host']))
    except KeyError:
        LOGGER.add('INFO', 'Default template returned. IDs: {}'.format(request.headers['Hosts']))
    return {}


async def analysis_result_v1(request: web.Request):
    """Returns bokeh analyzed stocks.
    :return HTMl/text"""
    filer = glob.glob(str(BASE_DIR) + '/ServiceProvider/templates/' + str(
        request.match_info['symbol']) + '*')
    filer = filer[0]
    payload = ""
    with open(filer) as file:
        for line in file.readlines():
            if "<title>" in line:
                line = line[0:13] + request.match_info['symbol'] + "</title>\n"
            payload += line
    LOGGER.add('INFO', 'Graph HTML sent.')
    return web.Response(text=escape(payload), content_type='text/html')


async def analyse_and_forward(request: web.Request):
    """Trigger the analysis of a stock."""
    code = request.match_info['symbol']
    model = TechModel()
    dict_val = model.analyse(code, from_live=False, in_json=True)
    header = {'symbol': code,
              'date_issued': datetime.now().strftime("%d-%m-%Y")}
    LOGGER.add('INFO', 'JSON file created, now sending...')
    return web.json_response(body=dict_val,
                             headers=header,
                             content_type='application/json')


async def get_news(request: web.Request):
    """Get news data for keywords."""
    request_data = await request.json()
    ft_model = FTArrangeWithWords(request_data['words'])
    ft_data = ft_model.get_summary().to_dict(orient='index')
    ft_data = json.dumps(ft_data)
    LOGGER.add('INFO', 'Converted to JSON news for words.')
    return web.json_response(body=ft_data,
                             content_type='application/json')


# async def get_feeder_data(request: web.Request):
#     """Fetch the data from ES or AlphaVantage APIs."""
#     return None


async def get_back_testing_data(request: web.Request):
    """To back-test the RL model."""
    code = request.match_info['symbol']
    fetch_model = FetchAllData()
    result = fetch_model.fetch_stock_data(code, in_pandas=False)
    LOGGER.add('INFO', "Successful in fetching data")
    result = json.dumps(result['hits'])
    LOGGER.add('INFO', "JSON conversion. {}".format(code))
    return web.json_response(body=result,
                             content_type='application/json')


async def get_train_data(request: web.Request):
    """In case train data is required fetch it for the given stock."""
    request_data = await request.json()
    es_model = FetchHistFromES(request_data['interval'],
                               request_data['timePeriod'])
    return_data = es_model.get_stock_data(request_data['symbol'],
                                          from_live=request_data['latest'])
    return_data['time'] = return_data['time'].dt.strftime('%Y-%m-%d')
    return_data = return_data.to_dict(orient='index')
    LOGGER.add('INFO', "Successful in fetching train data.")
    return_data = json.dumps(return_data)
    LOGGER.add('INFO', "Converted train data to JSON.")
    return web.json_response(body=return_data,
                             content_type='application/json')


async def get_nifty_data(request: web.Request):
    """Get the NIFTY last one year data, mainly used for news predictor."""
    request_data = await request.json()
    LOGGER.add('INFO', 'NIFTY Yearly Data sent. Request: {}'.format(request_data))
    return web.json_response(body=get_nifty_history(),
                             content_type='application/json')
