import json
from datetime import datetime
import pandas as pd
import glob
import Constants
from elasticsearch import Elasticsearch


def weekly_report_to_json():
    DAILY_DATA_FILES = [daily_data for daily_data in glob.glob(".\\resources\\*.csv*") if "WEEK" in daily_data]
    first_file_indicator = True
    for file in DAILY_DATA_FILES:
        if first_file_indicator:
            data = pd.read_csv(file)
            first_file_indicator = False
        else:
            temp_data = pd.read_csv(file)
            data = pd.concat([data, temp_data], axis=0)
    data.reset_index(inplace=True)
    data.to_json(".\\resources\\WEEKLY_JSON_TMP_{}.json".format(datetime.now().strftime('%d%m%Y'), orient='index'))


def insert_to_es_index():  # ES time outs while inserting the data.
    es = Elasticsearch(Constants.ES_URL, port=Constants.ES_PORT, retry_on_timeout=True, sniff_on_start=True,
                       sniff_on_connection_fail=True,
                       sniffer_timeout=60)
    file_name = glob.glob(".\\resources\\*.json*")[0]
    with open(file_name, 'r', encoding='utf-8') as f:
        data = json.loads(f.read())
    for index in range(len(data)):
        es.index(index='complete_data', body=data[str(index)])
        print("INDEX DONE: " + str(index))


