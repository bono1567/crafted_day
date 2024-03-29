"""Fetch the daily Equity data from NSE package."""
import os
from datetime import datetime

from json.decoder import JSONDecodeError
import pandas as pd
from pandas.errors import EmptyDataError
from nsetools import Nse
from LoggerApi.Logger import Logger


def reset_dict(get_column_names):
    """Reset the dictionary to an empty list.
    :return Dict with empty list as value of each key."""
    data_dict = {}
    for column in get_column_names:
        data_dict[column] = []
    return data_dict


class FetchNSEData(Logger):
    """NSE data retriever from the NSE module."""
    def __init__(self, batch_size=20):
        self.__batch_size = batch_size
        self.__model = Nse()
        super().__init__(FetchNSEData.__name__)
        self.add("INFO", self.__model)

    def save_daily_data(self, symbols=None, save=True):
        """Save the data locally in a CSV file."""
        if symbols is None:
            all_symbols = self.__model.get_stock_codes()
            all_symbols = list(all_symbols.keys())[1:]
        else:
            all_symbols = [symbol for symbol in symbols if self.__model.is_valid_code(symbol)]
            if all_symbols:
                raise EmptyDataError("NO SYMBOLS TO PROCESS")
        self.add('INFO', "Total number of stocks: {}".format(len(all_symbols)))
        get_column_names = self.__model.get_quote(all_symbols[0]).keys()
        self.add('INFO', "All the features: {}".format(get_column_names))

        data_dict = reset_dict(get_column_names)
        all_symbols = self.__if_exists(all_symbols)
        for symbol in all_symbols:
            try:
                equity_data = self.__model.get_quote(symbol)
                for column in get_column_names:
                    data_dict[column].append(equity_data[column])
                if (len(data_dict['symbol']) % self.__batch_size) == 0:
                    self.__save_to_csv(data_dict)
                    data_dict = reset_dict(get_column_names)
                self.add('INFO', "Symbol ingested: {} ".format(symbol))
            except IndexError:
                self.add('ERROR', "For symbol:{} the data doesn't exist.".format(symbol))
            except JSONDecodeError:
                self.add('ERROR', "JSON parser issue for {}".format(symbol))
        if save:
            self.__save_to_csv(data_dict)
        return data_dict

    def __if_exists(self, all_symbols):
        """Check if file exists. EQUITY rec file exists."""
        file_path_caps = os.path.abspath(
            os.path.join(__file__, "../../..")) + "//resources//EQUITY_REC_" \
                    + datetime.now().strftime('%d%m%Y') + '.csv '
        try:
            existing_df = pd.read_csv(file_path_caps)
            self.add('INFO', 'Pre-existing symbols:{}'.format(existing_df['symbol'].to_list()))
            all_symbols = [x for x in all_symbols if x not in existing_df['symbol'].to_list()]
            return all_symbols
        except (EmptyDataError, FileNotFoundError):  # Check if the file exists or is empty
            self.add('INFO', 'NO PRE-EXISTING RECORD.')
            return all_symbols
        except JSONDecodeError:
            return all_symbols

    def __save_to_csv(self, data_dict):
        """Save it in csv in a particular directory."""
        file_path_caps = os.path.abspath(os.path.join(__file__, "../../.."))\
                    + "//resources//EQUITY_REC_" \
                    + datetime.now().strftime('%d%m%Y') + '.csv'
        try:
            existing_df = pd.read_csv(file_path_caps)
        except (EmptyDataError, FileNotFoundError):  # Check if the file exists or is empty
            existing_df = pd.DataFrame(columns=[list(data_dict.keys())])
        data_frame = pd.DataFrame()

        for column in data_dict.keys():  # Add the values from dict
            data_frame[column] = data_dict[column]

        if existing_df.shape[0] == 0:
            existing_df = data_frame
        else:
            existing_df = pd.concat([existing_df, data_frame])

        existing_df.to_csv(file_path_caps, index=False)
        self.add('INFO', 'SAVED TO CSV. SIZE:{}'.format(existing_df.shape))
        del existing_df, data_frame
