"""Get stock data from ES index to build a model."""
import pandas as pd
from elasticsearch import Elasticsearch

import Constants
from LoggerApi.Logger import Logger


class FetchAllData(Logger):
    """ES data fetch class."""

    def __init__(self):
        super().__init__(FetchAllData.__name__, "WEEKLY_REPORT")
        self.elastic_search = Elasticsearch(Constants.ES_URL, port=Constants.ES_PORT,
                                            retry_on_timeout=True, sniff_on_start=True,
                                            sniff_on_connection_fail=True,
                                            sniffer_timeout=60)

    def fetch_stock_data(self, stock_indicator, in_pandas=True):
        """Fetch data from the respective index."""
        query = Constants.SEARCH_FOR_STOCK_DATA
        query["query"]["bool"]["must"][0]["term"]["symbol.keyword"]["value"] = stock_indicator
        if in_pandas:
            return self.__get_in_data_frame(self.fetch_stock_data(stock_indicator, False))
        return self.elastic_search.search(index=Constants.COMPLETE_DATA_INDEX, body=query)

    def __get_in_data_frame(self, json_data):
        """Convert the ES JSON data to Pandas DF
         :return pandas df"""
        self.add("INFO", "Total number of records: {}".format(json_data["hits"]["total"]["value"]))
        conversion_data = {}
        index = 0
        for record in json_data["hits"]["hits"]:
            conversion_data[str(index)] = record["_source"]
            index += 1
        final_data = pd.DataFrame.from_dict(conversion_data, orient='index')
        final_data['processingDate'] = pd.to_datetime(final_data['processingDate'])
        final_data.sort_values(by='processingDate', inplace=True)
        return final_data
