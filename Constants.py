# ES Constants
ES_URL = "localhost"
ES_PORT = 9200
COMPLETE_DATA_INDEX = "complete_data"
HIST_TECH_DATA_DAILY_INDEX = "hist_tech_daily_data"
HIST_TECH_DATA_WEEKLY_INDEX = "hist_tech_weekly_data"
PERF_DATA = "performance_data"

# SEARCH_FOR_HIST_STOCK_DATA =
BULK_INSERT = {
        "_index": "",
        "_id": "",
        "_source": ""
        }


SEARCH_FOR_STOCK_DATA = {
    "_source": ["symbol", "closePrice", "open", "dayHigh", "dayLow", "previousClose", "faceValue", "lastPrice",
                "extremeLossMargin", "pricebandlower", "pricebandupper", "companyName", "quantityTraded", "pChange",
                "totalBuyQuantity", "totalSellQuantity", "processingDate", "isExDateFlag"],
    "query": {
        "bool": {
            "must": [
                {
                    "term": {
                        "symbol.keyword": {
                            "value": ""
                        }
                    }
                }
            ]
        }
    }
}

# Alpha-vantage Constants
all_features = ['SMA', 'EMA', 'VWAP', 'MACD', 'STOCH', 'RSI', 'ADX', 'CCI', 'AROON', 'BBANDS', 'AD', 'OBV']
FEATURES = ['SMA', 'EMA', 'MACD']
KEY = "UA3OCB0CIG6WMCJ0"

"""There's no such thing as love without the anticipation of loss and " \
"that spectre of despair can be the engine of intimacy."""