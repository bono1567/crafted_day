import pandas as pd
from Harvester.HeadlineHarvester.DataRetriever import FTArrangement
from LoggerApi.Logger import Logger


class FTArrangeWithWords(Logger):
    __summary = []
    __title = []
    __date = []
    __total_data = []

    def __init__(self, words_for_search):
        super().__init__(FTArrangeWithWords.__name__)
        self.__words = words_for_search

    def get_summary(self, title=False):
        for word in self.__words:
            extraction_model = FTArrangement(word)
            extraction_with_summary_time = extraction_model.get_summary_date_api(True)
            extraction_with_summary, extraction_with_title = extraction_model.get_summary_for_w2v(True)
            self.__summary.extend(extraction_with_summary)
            self.__title.extend(extraction_with_title)
            self.__date.extend(extraction_with_summary_time['publishDate'].values.tolist())
            self.__total_data.extend(extraction_with_summary_time)
            self.add('INFO', 'Fetching SUMMARY_COMPLETE for {}'.format(word))
        data = pd.DataFrame()
        data['time'] = self.__date
        data['summary'] = self.__summary
        if title:
            data['title'] = self.__title

        return data

    def fetch_data_all(self):
        if len(self.__total_data) == 0:
            self.get_summary()
        return self.__total_data


# if __name__ == '__main__':
#     A = FTArrangeWithWords(['Modi', 'HDFC', 'Jamie Dimon'])
#     D = A.get_summary(True)
#
#     print(D.head())
