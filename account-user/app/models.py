#-*- encoding:utf-8 -*-

__author__ = "474416133@qq.com"

from db.models import attrs_wrapper  as aw
from db.models.attrs_wrapper import *


@model("USER")
class User(object):

    id = IntegerField()
    name = CharField()
    #info = field(User)

@model("UserInfo")
class UserInfo(object):
    id = IntegerField()
    name = CharField()
    #obj = field(User)

if __name__ == "__main__":
    print(IntegerField())
    #print(aw.attr.fields(User).id)
    user = User(1, "qiu")

    print(aw.attr.fields(User).id.name)





