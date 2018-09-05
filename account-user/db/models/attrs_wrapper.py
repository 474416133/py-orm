#-*- encoding:utf-8 -*-

__author__ = "474416133@qq.com"

import attr
import functools
import datetime
import weakref


NOTHING = attr.NOTHING

from .base import SingletonObject


class M3gr(SingletonObject):
    """
    medel meta manager , shut as M3gr
    """
    def __init__(self):
        self.metas = {}

    def push_meta(self, name, meta):
        self.metas[name] = meta

    def pull_meta(self, name):
        self.metas.pop(name)

    def has_meta(self, name):
        return name in self.metas

    def get(self, key):
        return self.metas.get(key)


def model(table_name=None):

    def _wrapper_model(cls):
        m3gr_instance = M3gr.instance()
        setattr(cls, "M3gr", m3gr_instance)
        _table_name = table_name or cls.__name__.split(".").pop().lower()

        setattr(cls, "table_name", _table_name)
        cls_obj =  attr.s()(cls)
        assert not m3gr_instance.has_meta(_table_name), u"model has exsit"
        m3gr_instance.push_meta(_table_name, cls_obj)
        return cls_obj

    return _wrapper_model



def field(pytype = None, verbose_name = None, primary_key=False,
          max_length=None, unique=False, null=False, db_column=None,
          default=NOTHING, validator=None, converter=None):
    _meta = {
                "verbose_name" : verbose_name,
                "primary_key" : primary_key,
                "max_length" : max_length,
                "unique" : unique,
                "null" : null,
                "db_column" : db_column
    }
    if isinstance(pytype, str):
        _meta.update("ref", pytype)
        return attr.ib(default=default, validator = validator, converter = converter, metadata=_meta)
    else :
        return attr.ib(default=default, validator=validator, converter=converter, metadata=_meta, type=pytype)


CharField = functools.partial(field, str)
IntegerField = functools.partial(field, int)
DateTimeField = functools.partial(field, datetime.datetime)
TimeStampField = functools.partial(field, int)



if __name__ == "__main__":
    @model(table_name="user")
    class User(object):
        name = CharField()


    user = User("qiu")
