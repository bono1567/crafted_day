"""Utility methods for Harvester module"""
import json
import glob
from datetime import datetime
import pandas as pd
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import RequestError
import Constants


def convert_to_same(timestamp):
    """Time stamp converter."""
    timestamp = timestamp[:1] + '/' + timestamp[1:3] + '/' + timestamp[-4:]
    return datetime.strptime(timestamp, '%d/%m/%Y')


def process_date(data):
    """:return List of dates"""
    final_date = []
    for timestamp in data:
        if len(str(timestamp)) == 8:
            final_date.append(datetime.strptime(str(timestamp), '%d%m%Y').strftime('%d-%b-%Y'))
        else:
            final_date.append(convert_to_same(str(timestamp)).strftime('%d-%b-%Y'))

    return final_date


def weekly_report_to_json():
    """Converts the CSV file to JSON for ES consumption."""
    daily_data_files = [daily_data for daily_data in
                        glob.glob(".\\resources\\*.csv*") if "WEEK" in daily_data]
    first_file_indicator = True
    data_weekly = None
    for file in daily_data_files:
        if first_file_indicator:
            data_weekly = pd.read_csv(file, low_memory=False)
            first_file_indicator = False
        else:
            temp_data = pd.read_csv(file)
            data_weekly = pd.concat([data_weekly, temp_data], axis=0)
    data_weekly.reset_index(inplace=True)
    data_weekly['isExDateFlag'] = 0.0
    data_weekly['processingDate'] = process_date(data_weekly['processingDate'])
    data_weekly.to_json(".\\resources\\WEEKLY_JSON_TMP_{}.json".format(
        datetime.now().strftime('%d%m%Y')), orient='index')


def insert_to_es_index(logger):  # ES time outs while inserting the data.
    """Insert the JSON data to ES."""
    elastic_search = Elasticsearch(Constants.ES_URL, port=Constants.ES_PORT,
                                   retry_on_timeout=True, sniff_on_start=True,
                                   sniff_on_connection_fail=True,
                                   sniffer_timeout=60)
    file_name = glob.glob(".\\resources\\*.json*")[0]
    with open(file_name, 'r', encoding='utf-8') as file_json:
        data = json.loads(file_json.read())
    for index in data.keys():
        try:
            elastic_search.index(index=Constants.COMPLETE_DATA_INDEX, body=data[index])
            logger.add("INFO", "INDEX DONE: " + data[index]['symbol'])
        except RequestError:
            logger.add("ERROR",
                       "Incorrect fields format in one of the entries in index: {}".format(index))


def join_nse_bse_listing(cwd, just_get=True):
    """Merge the NSE and BSE stocks list"""
    if just_get:
        final_data = pd.read_csv(cwd + "\\resources\\Final_Listing_2020.csv")
        return [final_data['Security Code'].values,
                final_data['Security Id'].values,
                final_data['Security Name'].values]
    nse = pd.read_csv(cwd + "\\resources\\NSE_Listing_2020.csv")
    nse_isin = nse['ISIN NUMBER'].values
    bse = pd.read_csv(cwd + "\\resources\\BSE_Listing_2020.csv")
    nse['ISIN NUMBER'] = nse['ISIN NUMBER'].astype(str)
    final_data = bse[bse['ISIN NUMBER'].isin(nse_isin)]
    final_data.to_csv(cwd + "\\resources\\Final_Listing_2020.csv", index=False)
    return [final_data['Security Code'].values,
            final_data['Security Id'].values,
            final_data['Security Name'].values]


def get_max_min_points(data, column_name):
    """This only used in Models.Graphs import so far"""
    if column_name not in data.columns.values:
        raise KeyError
    max_min_index = []
    data_list = data[column_name].values
    index_list = data['time'].values
    max_min_index.append(index_list[0])
    size = data.shape[0]
    if size <= 3:
        return data[['time', column_name]]
    for i in range(1, size - 1):
        if data_list[i - 1] < data_list[i] and data_list[i] > data_list[i + 1]:  # Maxima point
            max_min_index.append(index_list[i])
        if data_list[i - 1] > data_list[i] and data_list[i] < data_list[i + 1]:  # Minima point
            max_min_index.append(index_list[i])

    return data[['time', column_name]][data['time'].isin(max_min_index)]


if __name__ == '__main__':
    from LoggerApi.Logger import Logger
    LOGGER = Logger('MANUAL_INSERT_LOG')
    insert_to_es_index(LOGGER)
