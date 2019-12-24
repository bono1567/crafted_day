from Harvester.StockPriceHarvester.DataArrangement import ArrangedData
from Harvester.HeadlineHarvester.Weaver import DataWeaver

stocks_to_analyse = ['NSE:TATAMOTORS']
headline_words = [['vehicle', 'Tata', 'America', 'petrol', 'diesel', 'India']]

# ['volkswagen', 'cars', 'petrol', 'diesel', 'transport', 'vehicles', 'german', 'economy'],
                 # ['britannia', 'food', 'India', 'elections', 'Bombay', 'stocks'] ['ETR:VOW3', 'NSE:BRITANNIA',
A = ArrangedData("D")

# data = A.fetch(stocks_to_analyse, 1461)
# print(data[0].head())
for name, words_set in zip(stocks_to_analyse, headline_words):
    # x.to_csv('./resources/' + name + '.csv')
    B = DataWeaver(words_set, name)
    data = B.fetch(True)
    data.to_csv('./resources/' + name + '_NEWS' + '.csv')

