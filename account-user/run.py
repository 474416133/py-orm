#-*- encoding:utf-8 -*-

__author__ = "474416133@qq.com"

import asyncio
from app.main import create_app
import uvloop

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
loop = asyncio.get_event_loop()
app = create_app()

from aiohttp import web
web.run_app(app, host="127.0.0.1", port=8000)