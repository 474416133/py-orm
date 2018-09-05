#-*- encoding:utf-8 -*-

__author__ = "474416133@qq.com"

__all__ = ["InsertCommand", "UpdateCommand", "DeleteCommand", "BatchInsertCommand",
           "FetchCommand", "GetCommand", "CountCommand"]
from .async_conn_executor import (execute, executemany,\
                                    fetch, fetchone , count)

from .pg_parser import (parse_for_insert, parse_for_insertmany,
                        parse_for_update, parse_for_delete,
                        parse_for_get, parse_for_count)

from .base import Command

class InsertCommand(Command):
    executor = execute
    compiler = parse_for_insert

class UpdateCommand(Command):
    executor = execute
    compiler = parse_for_update

class DeleteCommand(Command):
    executor = execute
    compiler = parse_for_delete

class BatchInsertCommand(Command):
    executor = executemany
    compiler = parse_for_insertmany

class FetchCommand(Command):
    executor = fetch
    compiler = parse_for_get

class GetCommand(Command):
    executor = fetchone
    compiler = parse_for_get

class CountCommand(Command):
    executor = count
    compiler = parse_for_count