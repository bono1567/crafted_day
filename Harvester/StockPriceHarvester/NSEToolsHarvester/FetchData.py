from nsetools import Nse
from LoggerApi.Logger import Logger
import pandas as pd
from pandas.errors import EmptyDataError
import os
from datetime import datetime


def reset_dict(get_column_names):
    data_dict = {}
    for column in get_column_names:
        data_dict[column] = []
    return data_dict


class FetchNSEData(Logger):
    def __init__(self, batch_size=20):
        self.__BATCH_SIZE = batch_size
        self.__model = Nse()
        super().__init__(FetchNSEData.__name__)
        self.add("INFO", self.__model)

    def save_daily_data(self, symbols=None):
        if symbols is None:
            all_symbols = self.__model.get_stock_codes()
            all_symbols = list(all_symbols.keys())[1:]
        else:
            all_symbols = symbols
        self.add('INFO', "Total number of stocks: {}".format(len(all_symbols)))
        get_column_names = self.__model.get_quote(all_symbols[1]).keys()
        self.add('INFO', "All the features: {}".format(get_column_names))

        data_dict = reset_dict(get_column_names)
        all_symbols = self.__if_exists(all_symbols)
        for symbol in all_symbols:
            try:
                equity_data = self.__model.get_quote(symbol)
                for column in get_column_names:
                    data_dict[column].append(equity_data[column])
                if (len(data_dict['symbol']) % self.__BATCH_SIZE) == 0:
                    self.__save_to_csv(data_dict)
                    data_dict = reset_dict(get_column_names)
                self.add('INFO', "Symbol ingested: {} ".format(symbol))
            except IndexError:
                self.add('ERROR', "For symbol:{} the data doesn't exist.".format(symbol))
        self.__save_to_csv(data_dict)

    def __if_exists(self, all_symbols):
        FILE_PATH = os.path.abspath(os.path.join(__file__, "../../..")) + "//resources//EQUITY_REC_" \
                    + datetime.now().strftime('%d%m%Y') + '.csv'
        try:
            existing_df = pd.read_csv(FILE_PATH)
            self.add('INFO', 'Pre-existing symbols:{}'.format(existing_df['symbol'].to_list()))
            all_symbols = [x for x in all_symbols if x not in existing_df['symbol'].to_list()]
            return all_symbols
        except (EmptyDataError, FileNotFoundError):  # Check if the file exists or is empty
            self.add('INFO', 'NO PRE-EXISTING RECORD.')
            return all_symbols

    def __save_to_csv(self, data_dict):
        FILE_PATH = os.path.abspath(os.path.join(__file__, "../../..")) + "//resources//EQUITY_REC_" \
                    + datetime.now().strftime('%d%m%Y') + '.csv'
        try:
            existing_df = pd.read_csv(FILE_PATH)
        except (EmptyDataError, FileNotFoundError):  # Check if the file exists or is empty
            existing_df = pd.DataFrame(columns=[data_dict.keys()])
        data_frame = pd.DataFrame()
        already_present = existing_df['symbol']

        for column in data_dict.keys():  # Add the values from dict
            data_frame[column] = data_dict[column]

        if existing_df.shape[0] == 0:
            existing_df = data_frame
        else:
            existing_df = pd.concat([existing_df, data_frame])

        existing_df.to_csv(FILE_PATH, index=False)
        self.add('INFO', 'SAVED TO CSV. SIZE:{}'.format(existing_df.shape))
        del existing_df, data_frame


