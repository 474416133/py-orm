#-*- encoding:utf-8 -*-

__author__ = "474416133@qq.com"

__all__= ["CharField", "IntegerField", "DateField", "DateTimeField",
          "BooleanField"]



from ._make import Field

class CharField(Field): pass
class IntegerField(Field): pass
class DateField(Field): pass
class DateTimeField(Field): pass
class BooleanField(Field):pass








