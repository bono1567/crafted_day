"""Project view for crafted day."""
from aiohttp import web


async def index(request):
    """Index view for the web-app."""
    return web.Response(text='Crafted Day Project.')
