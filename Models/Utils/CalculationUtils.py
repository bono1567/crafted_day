import Constants
from Harvester.StockPriceHarvester.DataArrangement import FetchHistFromES
from LoggerApi.Logger import Logger

logger = Logger(__file__, 'CALCULATION_LOG')


class RiskRewardForStock:
    ratio = 0

    def get_ratio(self, amount_invested, expected_book_price, stop_loss_amount):
        if amount_invested > expected_book_price:
            logger.add("ERROR", "You are expecting a loss from your investment")
            return None
        if stop_loss_amount > amount_invested:
            logger.add("ERROR", "Your stop loss amount is greater than the amount invested.")
            return None
        self.ratio = (expected_book_price - amount_invested) / (amount_invested - stop_loss_amount)
        return self.ratio

    def get_rating(self, amount_invested, expected_book_price, stop_loss_amount):
        if self.ratio == 0:
            self.get_ratio(amount_invested, expected_book_price, stop_loss_amount)
        if self.ratio > 4.0:
            return Constants.HL
        if self.ratio > 3.0:
            return Constants.AL
        if self.ratio > 2.0:
            return Constants.AA
        return Constants.LH


def get_max_min_points(data, column_name):
    if column_name not in data.columns.values:
        raise KeyError
    max_min_index = []
    data_list = data[column_name].values
    index_list = data['time'].values
    size = data.shape[0]
    if size <= 3:
        return data[['time', column_name]]
    for i in range(1, size - 1):
        if data_list[i - 1] < data_list[i] and data_list[i] > data_list[i + 1]:  # Maxima point
            max_min_index.append(index_list[i])
        if data_list[i - 1] > data_list[i] and data_list[i] < data_list[i + 1]:  # Minima point
            max_min_index.append(index_list[i])

    return data[['time', column_name]][data['time'].isin(max_min_index)]



# if __name__ == '__main__':
#     model = FetchHistFromES('D', 100)
#     data = model.get_stock_data('ASIANHOTNR', from_live=False)
#     print(get_max_min_points(data, 'close'))





