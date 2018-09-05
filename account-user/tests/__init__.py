"""
account-user tests
"""
import time
import datetime

TIMESTAPM = time.time()

ID = lambda : int((time.time() - TIMESTAPM) * 1000)

from  db.models import Model,  CharField, IntegerField, DateField, BooleanField
from  db.models.command import *

class Attribute(object):

    def __init__(self, name):
        self.name = name

    def __get__(self, instance, ower):
        print("getting")
        if instance:
            return instance.__dict__[self.name]
        return self

    def __set__(self, instance, value):
        print("setting")
        instance.__dict__[self.name] = value


class User(Model):

    #id = Attribute("id")
    #name = Attribute("name")
    id = IntegerField(verbose_name="id", primary_key=True)
    name = CharField(verbose_name="name")

    class Meta:
        default_table_name = "test"

    @name.validator
    def test_name(self, value):
        if self.name == "qiu":
            raise Exception("rrrr")

    @id.default
    def default_id(self):
        return ID()


@User.name.validator
def test_name2(value):
    print("%s"%value)


class AccountUser(Model):
    id = IntegerField(verbose_name="id", primary_key=True)
    username = CharField(verbose_name="姓名")
    password = CharField(verbose_name="密码")
    created_time = DateField(verbose_name="创建时间")
    is_active = BooleanField(verbose_name="状态")
    last_login_time = DateField(verbose_name="最后登陆时间")
    last_login_ip = IntegerField(verbose_name="ip")

    class Meta:
        default_table_name = "account_user"

    @id.default
    def default_id(self):
        return ID()


import asyncpg
import asyncio
import uvloop

loop = uvloop.new_event_loop()
asyncio.set_event_loop(loop)

pool = loop.run_until_complete(asyncpg.create_pool("postgres://postgres:postgres@localhost:5432/edu"))

async def test_insert(_pool, obj):
    async with _pool.acquire() as conn:
        command = InsertCommand(obj)
        await command.execute(conn)

async def test_inserts(_pool, comms):
    async with _pool.acquire() as conn:
        async with conn.transaction():
            print(comms.__dict__)
            await comms.execute(conn)

if __name__ == "__main__":

    time.sleep(6)
    print("start=========")
    user = User()
    user.id = ID()
    user.name = "qiu1"


    user6 = User()
    user6.id = ID() + 2
    user6.name = "qiusdf"

    users = []
    users.append(user)
    users.append(user6)


    account_user = AccountUser()
    account_user.username = "svenqiu56"
    account_user.password = "asdfsdfsfd"
    account_user.last_login_ip = 343
    account_user.last_login_time = datetime.datetime.now()
    account_user.created_time = datetime.datetime.now()
    account_user.is_active = True

    #print(InsertCompiler()(user))
    #print(UpdateCompiler()(user))
    #print(DeleteCompiler()(user))
    #loop.run_until_complete(test_insert(pool, user))
    #loop.run_until_complete(test_insert(pool, user))
    cc = CC()
    cc.add_command(BatchInsertCommand(users))
    cc.add_command(InsertCommand(account_user))
    loop.run_until_complete(test_inserts(pool, cc))




