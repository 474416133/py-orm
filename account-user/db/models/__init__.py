#-*- encoding:utf-8 -*-

__author__ = "474416133@qq.com"

import inspect

from ._make import Model,ModelRelatedEntity
from .fields import *
from .error import *
#from .compiler.pg import *
from .excutor import AWriteSqlExcutor, AReadSqlExcutor



class ASyncManager(ModelRelatedEntity):


    @property
    def pool(self):
        return self.model._meta_mgr.pool

    async def get_conn(self):
        return await self.pool.acquire()


    async def get(self, pk=None, sql=None, params=None):
        model_cls = self.model

        if pk:
            _pk = model_cls.pk.column_name or model_cls.pk.name
            sql = "SELECT %s FROM %s WHERE %s = $1 "%(",".join(model_cls.get_column_names()),\
                                                     model_cls.get_table_name,\
                                                      _pk)

            params = [1]

        if not sql:
            raise ArgsError("arg `pk` or `sql` must present ")

        ret = await  self.query(sql, params)
        return model_cls(**dict(ret))


    async def create(self, instance=None, **kwargs):
        if not instance:
            instance = self.model(**kwargs)

        instance = self.model(**kwargs)
        sql, params = "", "" #InsertCompiler()(instance)
        await self.execute(sql, params)


    async def bulk_create(self, objs):
        sql, params = "", "" #BatchInsertCompiler()(objs)
        await self.execute(sql, params)


    async def get_or_create(self, default=None, **kwargs):
        pass

    async def update(self, instance=None, fields=None, **kwargs):
        if not instance:
            instance = self.model(**kwargs)
        sql, params="", "" #UpdateCompiler()(instance, fields)
        await self.execute(sql, params)

    async def update_or_create(self, *args, **kwargs):
        pass

    async def delete(self, instance=None, **kwargs):
        if not instance:
            instance = self.model(**kwargs)
        sql, params = "", "" # DeleteCompiler()(instance)
        await self.execute(sql, params)

    async def query(self, sql, params):
        async with self.get_conn() as conn:
                await AReadSqlExcutor()(conn, sql, params)

    async def execute(self, sql, params):
        async with self.get_conn() as conn:
            async with conn.transaction():
                await AWriteSqlExcutor()(conn, sql, params)





