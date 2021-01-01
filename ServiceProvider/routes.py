from ServiceProvider.views import index, analysis_result_v1, \
    analyse_and_forward, get_news, get_train_data


def setup_routes(app):
    app.router.add_get("/", index)
    app.router.add_get("/admin", index)
    app.router.add_route('GET', '/graph/{symbol}', analysis_result_v1)
    app.router.add_route('GET', '/analyse/{symbol}', analyse_and_forward)
    app.router.add_route('GET', '/trainData/{symbol}', get_train_data)
    app.router.add_route('POST', '/getNews/', get_news)
