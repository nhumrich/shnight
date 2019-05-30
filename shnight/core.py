import asyncio
from shnight.routes import routes
from aiohttp import web
from shnight.controller import run_always
import aiohttp_cors


async def on_startup(app):
    asyncio.create_task(run_always())


def main():
    app = web.Application()
    app.add_routes(routes)
    cors = aiohttp_cors.setup(app, defaults={
        "*": aiohttp_cors.ResourceOptions(
            allow_credentials=True,
            expose_headers="*",
            allow_headers="*",
        )
    })
    for route in list(app.router.routes()):
        cors.add(route)
    app.on_startup.append(on_startup)
    web.run_app(app)
