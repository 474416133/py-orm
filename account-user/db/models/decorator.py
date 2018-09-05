#-*- encoding:utf-8 -*-

__author__ = "474416133@qq.com"

import inspect

class _Singleton(type):
    """
    单例模式
    """

    def __call__(cls, *args, **kwargs):

        if not hasattr(cls, "_instance"):
            cls._instance = super().__call__(*args, **kwargs)
        return cls._instance

class SingletonObject(metaclass=_Singleton):

    @classmethod
    def instance(cls):
        return cls()

def singleton(maybe_class):
    """
    单例模式
    :param maybe_class:
    :return:
    """
    if not inspect.isclass(maybe_class):
        return maybe_class

    if not hasattr(maybe_class, '__instance'):
        maybe_class.__instance = maybe_class()

    def __new__(cls, *args, **kwargs):
        return cls.__instance

    maybe_class.__new__ = __new__
    return maybe_class

@singleton
class A(object):pass

if __name__ == "__main__":
    a = A()
    b = A()
    print(a==b)