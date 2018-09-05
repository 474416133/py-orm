#-*- encoding:utf-8 -*-

__author__ = "474416133@qq.com"


from .fields import Field
from .error import *

class Query(object):
    """
    数据操作对象
    """

    def __init__(self, sql=None, params=None):

        self._for_write = False
        self._sql = sql
        self._params = params
        self._is_empty = True
        self._querys = None
        self._model = None


    @property
    def is_empty(self):
        return self._is_empty


    def query(self, sql, params):
        """
        new query
        :param sql:
        :param params:
        :return:
        """
        query_cls = self.__class__
        return query_cls(sql, params)


    def count(self, field=None):
        """
        统计记录数
        :param field:
        :return:
        """
        return self.query(self._build_count_sql(field), self._params)

    def  _build_count_sql(self, field=None):
        """
        根据当前query对象解析count语句
        :param field:
        :return:
        """
        if self._for_write is True:
            raise QueryOpError(u"write query can't read")


        if isinstance(field, str):
            if not self._sql:
                raise ArgsError("query is unvilable")

            sql_from_index = self._sql.lower().find("from")
            return "SELECT COUNT(%s) %s" %(field, self._sql[sql_from_index:])

        elif isinstance(field, Field):
            if  self._model != field.model:
                raise ModelNotMatchError("%s != %s"%(getattr(self._model, "__class__"), getattr(field.model, "__class__")))
            pk = field.model.pk
            pk_column = pk.column_name or pk.name
            table_name = field.model.get_table_name()
            if self._is_empty:
                return "SELECT COUNT(%s) FROM %s"%(pk_column, table_name)

