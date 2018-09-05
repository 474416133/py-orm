#-*- encoding:utf-8 -*-

__author__ = "474416133@qq.com"

__all__ = ["execute", "executemany", "fetch", "fetchone", "count"]

async def execute(conn, sql, params):
    """
    写操作（单条）
    :param conn:
    :param sql:
    :param params:
    :return:
    """
    print("sql:%s, params:%s"%(sql, params))
    params = params or ()
    await conn.execute(sql, *params)

async def executemany(conn, sql, params):
    """
    写操作(多条)
    :param conn:
    :param sql:
    :param params:
    :return:
    """
    params = params or ()
    print("sql:%s, params:%s"%(sql, params))
    await conn.executemany(sql, params)

async def fetch(conn, sql, params):
    """
    读操作
    :param conn:
    :param sql:
    :param params:
    :return:
    """
    params = params or ()
    return await conn.fetch(sql, *params)

async def fetchone(conn, sql, params):
    """
    单条读取操作
    :param conn:
    :param sql:
    :param params:
    :return:
    """
    params = params or ()
    return await conn.fetchone(sql, *params)

async def count(conn, sql, params):
    """
    统计
    :param conn:
    :param sql:
    :param params:
    :return:
    """
    params = params or ()
    return await conn.fetchval(sql, *params)

