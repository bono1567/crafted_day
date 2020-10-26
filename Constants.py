# ES Constants
ES_URL = "localhost"
ES_PORT = 9200
COMPLETE_DATA_INDEX = "complete_data"
HIST_TECH_DATA_DAILY_INDEX = "hist_tech_daily_data"
HIST_TECH_DATA_WEEKLY_INDEX = "hist_tech_weekly_data"
PERF_DATA = "performance_data"
INSERTION_OFFSET = 100
SEARCH_FOR_HIST_STOCK_DATA = {
    "size": 1500,
    "query": {
        "bool": {
            "filter": {
                "term": {
                    "code": 0
                }
            }
        }
    }
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
all_features = ['SMA', 'EMA', 'VWAP', 'MACD', 'STOCH', 'RSI', 'ADX', 'CCI', 'AROON', 'BBANDS', 'AD', 'OBV', 'MFI']
FEATURES = ['MACD', 'MFI', 'ADX']
KEY = "UA3OCB0CIG6WMCJ0"

"""There's no such thing as love without the anticipation of loss and " \
"that spectre of despair can be the engine of intimacy."""

# Risk symbols
HL = "HRE-LRI"  # High return, low risk
AL = "ARE-LRI"  # Average return, low risk
AA = "ARE-ARI"  # Average return, average risk
LH = "LRE-HRI"  # Low return, high risk
TOTAL_UNITS_TO_BUY = 20
