"""The web-app starter. """
from aiohttp import web
from ServiceProvider.routes import setup_routes

app = web.Application()
setup_routes(app)
web.run_app(app)
