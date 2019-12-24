from Harvester.StockPriceHarvester.DataArrangement import ArrangedData
from Harvester.HeadlineHarvester.Weaver import DataWeaver
stocks_to_analyse = ['ETR:VOW3', 'NSE:BRITANNIA', 'NSE:TATAMOTORS']
headline_words = [['volkswagen', 'cars', 'petrol', 'diesel', 'transport', 'vehicles', 'german', 'economy'],
                  ['britannia', 'food', 'India', 'elections', 'Bombay', 'stocks'],
                  ['vehicles', 'Tata', 'America', 'petrol', 'diesel', 'India']]

A = ArrangedData("D")

data = A.fetch(stocks_to_analyse, 1461)
print(data[0].head())
for name, x, words_set in zip(stocks_to_analyse, data, headline_words):
    x.to_csv('./resources/' + name + '.csv')
    B = DataWeaver(words_set, name)
    data = B.fetch(True)
    data.to_csv('./resources/' + name + '_NEWS' + '.csv')



