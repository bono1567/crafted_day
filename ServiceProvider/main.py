"""The web-app starter. """
import ssl

from aiohttp import web

from ServiceProvider.middlewares import setup_middleware
from ServiceProvider.routes import setup_routes
from ServiceProvider.settings import setup_config

app = web.Application()
setup_routes(app)
setup_middleware(app)
setup_config(app)
# app.on_startup - On application start-up
# app.on_cleanup
ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
ssl_context.load_cert_chain('/apps/cert/crafted_certificate.crt', '/apps/cert/crafted_key.key')
web.run_app(app, ssl_context=ssl_context)
