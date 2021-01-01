"""Application config for the web-app."""
import pathlib

import aiohttp_jinja2
import jinja2
import yaml

BASE_DIR = pathlib.Path(__file__).parent.parent
CONFIG_PATH = BASE_DIR / 'config' / 'application.yaml'


def get_config(path):
    """Fetches the config from yaml file and set jinja path."""
    with open(path) as f:
        configuration = yaml.safe_load(f)

    return configuration


def setup_config(app):
    """Set-up aiohtpp-jinja template path."""
    app.router.add_static('/static/',
                          path=BASE_DIR / 'ServiceProvider' / 'static',
                          name='static')
    aiohttp_jinja2.setup(app,
                         loader=jinja2.FileSystemLoader(
                             str(BASE_DIR / 'ServiceProvider' / 'templates')))
    app['config'] = get_config(CONFIG_PATH)
