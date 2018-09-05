#-*- encoding:utf-8 -*-

__author__ = "474416133@qq.com"

class ASqlExcutor(object):
    """
    sql执行器
    """

    #sql编译器：model tranfa to sql,pamrams
    complier = None

    def __init__(self, complier):
        self.complier = complier

    async  def __call__(self, conn=None, obj=None, sql_params=None):

        if sql_params is not None:
            sql, params = sql_params
        elif obj is not None:
            sql, params = self._do_compile(obj)
        else:
            raise Exception("not avail sql, params")

        return await self._excute(conn, obj, params)


    def _do_compile(self, obj):
        return  self.complier(obj)

    async def _excute(self, conn, sql, params):
        raise  NotImplemented


class AWriteSqlExcutor(ASqlExcutor):
    """
    数据库写执行器
    包括 insert/update/delete
    """

    async def _excute(self, conn, sql, params):
        return await conn.excute(sql, params)


class AReadSqlExcutor(ASqlExcutor):
    """
    读执行器, select ...
    """
    async  def _excute(self, conn, sql, params):
        return await conn.fetch(sql, params)




if __name__ == "__main__":
    call = AReadSqlExcutor.__call__
    import inspect
    call_sign = inspect.signature(call)
    print(call_sign.parameters)
    #print(hasattr(AReadSqlExcutor, "__call__"))














