"""aiohttp utils"""
import json
import pandas as pd


def get_nifty_history(in_json=True):
    """Returns on year static NIFTY data"""
    data = pd.read_csv("..\\Harvester\\resources\\NIFTY_DATA.csv")
    data['time'] = pd.to_datetime(data['Date'], format="%d-%b-%Y")
    data.drop(['Date'], axis=1, inplace=True)
    data['time'] = data['time'].dt.strftime('%Y-%m-%d')
    if in_json:
        data = pd.DataFrame.to_dict(data, orient='index')
        return json.dumps(data)
    return data
