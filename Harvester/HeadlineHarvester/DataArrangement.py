import numpy as np
import pandas as pd
from Harvester.HeadlineHarvester.DataRetriever import FTArrangement


class FTArrangeWithWords:
    __summary = []
    __title = []
    __date = []
    __total_data = []

    def __init__(self, words_for_search):
        for word in words_for_search:
            extraction_model = FTArrangement(word)
            extraction_with_summary_time = extraction_model.getSummaryDateAPI()
            extraction_with_summary, extraction_with_title = extraction_model.getSummaryForW2V(True)
            self.__summary.extend(extraction_with_summary)
            self.__title.extend(extraction_with_title)
            self.__date.extend(extraction_with_summary_time['publishDate'].values.tolist())
            self.__total_data.extend(extraction_with_summary_time)

    def getSummary(self, title=False):
        data = pd.DataFrame()
        data['time'] = self.__date
        data['summary'] = self.__summary
        if title:
            data['title'] = self.__title

        return data

    def fetchDataAll(self):
        return self.__total_data

if __name__ == '__main__':
    A = FTArrangeWithWords(['Modi', 'Jamie Dimon', 'India', 'TATA'])
    D = A.getSummary(False)

    print(D.head())
