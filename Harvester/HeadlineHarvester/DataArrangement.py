"""Financial Times conversion to acceptable format."""
import pandas as pd
from Harvester.HeadlineHarvester.DataRetriever import DataArrangement
from LoggerApi.Logger import Logger

LOGGER = Logger(__file__)


class FTArrangeWithWords:
    """FT data arrangement class."""

    def __init__(self, words_for_search):
        self.__words = words_for_search
        self.__summary = []
        self.__titles = []
        self.__date = []
        self.__total_data = []

    def get_summary(self):
        """Get the summary for the input words_for_search."""

        for word in self.__words:
            extraction_model = DataArrangement(word)
            extraction_with_summary_time = extraction_model.get_summary_date_api(True)
            extraction_with_summary, extraction_with_title =\
                extraction_model.get_summary_for_w2v(True)
            self.__summary.extend(extraction_with_summary)
            self.__titles.extend(extraction_with_title)
            self.__date.extend(extraction_with_summary_time['publishDate'].values.tolist())
            self.__total_data.extend(extraction_with_summary_time)
            LOGGER.add('INFO', 'Fetching SUMMARY_COMPLETE for {}'.format(word))
        data = pd.DataFrame()
        data['time'] = self.__date
        data['summary'] = self.__summary
        if self.__titles:
            data['title'] = self.__titles

        return data

    def fetch_data_all(self):
        """ Fetch all the data."""
        if self.__total_data:
            self.get_summary()
        return self.__total_data


# if __name__ == '__main__':
#     A = FTArrangeWithWords(['Modi', 'HDFC', 'Jamie Dimon'])
#     D = A.get_summary(True)
#
#     print(D.head())
