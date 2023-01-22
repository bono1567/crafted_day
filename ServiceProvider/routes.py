"""THe URL routes are added here."""
from ServiceProvider.views import get_nifty_data, analyse_and_forward, analysis_result_v1,\
    index, get_back_testing_data, get_news, get_train_data


def setup_routes(app):
    """The API paths"""
    app.router.add_get("/", index)
    app.router.add_get("/admin", index)
    app.router.add_get("/niftyHistory", get_nifty_data)
    app.router.add_route('GET', '/getBackTesting/{symbol}', get_back_testing_data)
    app.router.add_route('GET', '/graph/{symbol}', analysis_result_v1)
    app.router.add_route('GET', '/analyse/{symbol}', analyse_and_forward)
    app.router.add_route('POST', '/trainData/', get_train_data)
    app.router.add_route('POST', '/getNews/', get_news)
