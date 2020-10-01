import glob
import os
import pandas as pd
from LoggerApi.Logger import Logger
"""For the Models modules we will be using this to extract the data collected in the given time-frame. Work till ES 
solution is made. """


class FetchAllData(Logger):
    RESOURCE_PATH = os.path.dirname(os.path.dirname(os.path.dirname(__file__))) + "/resources/*WEEK*"
    ALL_FILES = [x for x in glob.glob(RESOURCE_PATH) if "JSON" not in x]

    def __init__(self):
        super().__init__(FetchAllData.__name__, 'WEEKLY_REPORT')
        final_data = pd.read_csv(self.ALL_FILES[0])
        self.add("INFO", "File processed: {}".format(self.ALL_FILES[0]))
        first_indicator = True
        for file in self.ALL_FILES:
            if first_indicator:
                first_indicator = False
                continue
            final_data = pd.concat([final_data, pd.read_csv(file)], axis=0)
            self.add("INFO", "File processed: {}".format(file))
        self.add("INFO", "All files fetched.")
        self.all_data = final_data
        del final_data

    def get_stock_data(self, stock_indicator):
        stock_indicator = stock_indicator.upper()
        data = self.all_data[self.all_data['symbol'] == stock_indicator]
        if data.empty:
            self.add("ERROR", "Not indicator named '{}' exists. ".format(stock_indicator))
            return data
        self.add("INFO", "Data for '{}' extracted.".format(stock_indicator))
        return data


A = FetchAllData()







