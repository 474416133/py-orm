#-*- encoding:utf-8 -*-

__author__ = "474416133@qq.com"

import weakref

from contextlib import contextmanager
class Cached(type):

    def __init__(self, *args, **kwargs):
        print("Cached init..:%s,%s"%(args, kwargs))
        #super().__init__(*args, **kwargs)
        init_method = super().__init__
        init_method0 = super(Cached, self).__init__
        print (init_method == init_method0)
        init_method(*args, **kwargs)
        self.__cache = weakref.WeakValueDictionary()

    def __call__(self, *args):
        print("Cached __call__")
        if args in self.__cache:
            return self.__cache[args]
        else:
            obj = super().__call__(*args)
            print ("dict:%s"%obj.__dict__)
            self.__cache[args] = obj
            return obj


class Spam(metaclass=Cached):

    def __init__(self, name):
        print("Spam init")
        self.name = name

    def do_raise(self):
        raise NotImplemented


class _Singleton(type):

    instance = None

    def __call__(self, *args, **kwargs):
        if not _Singleton.instance:
            _Singleton.instance = super().__call__(*args, **kwargs)

        return _Singleton.instance

class A(object,metaclass=_Singleton):

    @classmethod
    def pay(self, name=None):
        print("self:%s"%self)

if __name__ == "__main__":

    print("+++++++++++++++++++++++++=")
    a = A()
    b = A()
    #print(a.mro())
    print(a==b)
    A.pay()
    #s = Spam("name")
    #s.do_raise()
    #s1 = Spam("s1")

