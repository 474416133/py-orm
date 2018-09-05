#-*- encoding:utf-8 -*-

__author__ = "474416133@qq.com"

import json
import asyncpg
import datetime

class RecordEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, asyncpg.Record):
            return dict(o)
        elif isinstance(o, datetime.datetime):
            return o.strftime("%Y-%m-%d %H:%M:%S.%s")
        return super().default(o)


async def get_account_user(pool):
    async with pool.acquire() as con:
        users =  await con.fetch("SELECT * FROM account_user")
        print("users:%s"%users)
        return users
