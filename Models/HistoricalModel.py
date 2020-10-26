from Harvester.StockPriceHarvester.DataArrangement import FetchHistFromES
from LoggerApi.Logger import Logger
from Models.Utils.CalculationUtils import RiskRewardForStock, get_max_min_points
from VisualisationSector.Graphs import VisualAnalysis


class TechModel(Logger):
    INTERVAL = 'D'
    TIME_PERIOD = 365 * 2
    p_items = {}

    def __init__(self):
        super().__init__(TechModel.__name__, 'TECH_LOG')
        self.es_model = FetchHistFromES(self.INTERVAL, self.TIME_PERIOD)
        self.rr_model = RiskRewardForStock()
        self.graph_model = VisualAnalysis()

    def analyse(self, stock_indicator, from_live=False):
        annual_data = self.__get_stock_data(stock_indicator, from_live)
        self.p_items['cd_stick'] = self.graph_model.get_candlestick(annual_data, show_graph=False)
        self.p_items['price'] = self.graph_model.get_trend_line(annual_data, show_graph=False)
        self.p_items['volume'] = self.graph_model.get_volume_hist(annual_data, show_graph=False)

        self.graph_model.show_all(self.p_items, stock_indicator)

        # max_min_points = get_max_min_points(annual_data, 'adjusted_close')
        # Formulate a way to get expected returns and stop-loss percentage

        expected_return_percentage, stop_loss_percentage = (0.2, 0.005)
        self.__set_risk_reward(annual_data, expected_return_percentage, stop_loss_percentage)

    def __get_stock_data(self, stock_indicator, from_live):
        return self.es_model.get_stock_data(stock_indicator, from_live)

    def __set_risk_reward(self, annual_data, exp_rw, stop_loss):
        closed_value = annual_data.iloc[-1]['adjusted_close']
        expected_book_price = closed_value + (closed_value * exp_rw)
        stop_loss_amount = closed_value - (closed_value * stop_loss)
        self.rr_rating = self.rr_model.get_rating(closed_value, expected_book_price, stop_loss_amount)
        self.rr_ratio = self.rr_model.ratio
        self.add("INFO", "R/R calculated: {} (Date of calculation: {})".format(self.rr_ratio,
                                                                               annual_data.iloc[-1]['time']))


if __name__ == "__main__":
    A = TechModel()
    # A.analyse('TITAN')
    A.analyse('ASIANHOTNR', from_live=False)
