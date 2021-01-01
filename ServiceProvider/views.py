"""Project view for crafted day."""
import glob
import aiohttp_jinja2
from aiohttp import web
from datetime import datetime
from LoggerApi.Logger import Logger
from Models.HistoricalModel import TechModel
from ServiceProvider.settings import BASE_DIR

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
    FILE = glob.glob(str(BASE_DIR) + '/ServiceProvider/templates/' + str(request.match_info['symbol']) + '*')
    FILE = FILE[0]
    payload = ""
    with open(FILE) as file:
        for line in file.readlines():
            if "<title>" in line:
                line = line[0:13] + request.match_info['symbol'] + "</title>\n"
            payload += line
    LOGGER.add('INFO', 'Graph HTML sent.')
    return web.Response(text=payload, content_type='text/html')


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
    return None


async def get_feeder_data(request: web.Request):
    """Fetch the data from ES or AlphaVantage APIs."""
    return None


async def get_back_testing_data(request: web.Request):
    """To back-test the RL model."""
    return None


async def get_train_data(request: web.Request):
    """In case train data is required fetch it for the given stock."""
    return None




