from pathlib import Path

from aiohttp import web

from .settings import Settings
from .views import index, get_account_user

import asyncpg

THIS_DIR = Path(__file__).parent
BASE_DIR = THIS_DIR.parent

import db
def setup_routes(app):
    app.router.add_get('/', index, name='index')
    app.router.add_get('/account_users', get_account_user, name='account_users')


async def create_aiopg(app):
    app["pg_engine"] = await asyncpg.create_pool("postgres://postgres:postgres@localhost:5432/edu")

async def close_aiopg(app):
    await app["pg_engine"].close()


def create_app():
    app = web.Application()
    settings = Settings()
    app.update(
        name='account-user',
        settings=settings
    )

    setup_routes(app)
    app.on_cleanup.append(close_aiopg)
    app.on_startup.append(create_aiopg)

    return app
