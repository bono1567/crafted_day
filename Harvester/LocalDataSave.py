from Harvester.StockPriceHarvester.DataArrangement import ArrangedData

stocks_to_analyse = ['ETR:VOW3', 'NSE:BRITANNIA', 'NSE:TATAMOTORS']

A = ArrangedData("D")
data = A.fetch(stocks_to_analyse, 1461)
print(data[0].head())
for name, x in zip(stocks_to_analyse, data):
    x.to_csv('./resources/' + name + '.csv')



