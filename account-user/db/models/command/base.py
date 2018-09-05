#-*- encoding:utf-8 -*-

__author__ = "474416133@qq.com"

import functools

import inspect
from collections import Iterator
from ..error import *


def make_execute_async():
    """
    生成协程
    :return:
    """
    async def execute(self, conn):
        excutor = self.__class__.executor
        return await excutor(conn, *self.execute_args)
    return execute


def make_execute_sync():
    """
    生成execute
    :return:
    """
    def execute(self, conn):
        excutor = self.__class__.executor
        return excutor(conn, *self.execute_args)
    return execute


class CommandBuilder(type):
    """
    自动生成execute方法
    """

    def __new__(cls, name, bases, attrs):
        super_new = super().__new__
        cls_executor = attrs.get("executor")
        if not cls_executor:
            return super_new(cls, name, bases, attrs)
        if "execute" in attrs:
            return super_new(cls, name, bases, attrs)
        elif inspect.iscoroutine(cls_executor) or \
            inspect.iscoroutinefunction(cls_executor):
            attrs["execute"] = make_execute_sync()
        else:
            attrs["execute"] = make_execute_async()

        return super_new(cls, name, bases, attrs)


class Command(metaclass=CommandBuilder):
    compiler = None
    executor = None

    def __init__(self, instance=None, fields=None, sql=None, params=None):
        cls_ = self.__class__
        if instance:
            sql, params = cls_.compiler(instance, fields)

        self.execute_args = sql, params
        self.is_coroutine_obj = cls_.iscoroutine()


    def add_command(self, command):
        raise NotImplemented

    def remove_command(self, command):
        raise NotImplemented

    @classmethod
    def iscoroutine(cls):
        if not cls.executor:
            return False
        elif inspect.iscoroutinefunction(cls.executor):
            return True
        elif inspect.iscoroutine(cls.executor):
            return True
        else:
            return False


def make_cc_execute_async():
    async def execute(self, conn):
        ret = []
        for command in self.commands:
            if command.is_coroutine_obj :
                ret.append(await command.execute(conn))
            else:
                ret.append(command.execute(conn))
        return ret
    return execute

def make_cc_execute_sync():
    def execute(self, conn):
        ret = []
        for command in self.commands:
            ret.append(command.execute(conn))
        return ret
    return execute


class ComposteCommand(Command):
    """
    组合命令，用于事物
    """

    def __init__(self, commands=None):
        self.commands = commands if isinstance(commands, Iterator) and \
                                    all(map(lambda x: isinstance(x, Command), commands)) \
                                else []

        self.is_coroutine_obj = None

    def add_command(self, command):
        """
        添加命令
        :param command:
        :return:
        """
        assert  isinstance(command, Command), u"command must be a Command object"
        assert hasattr(command, "execute"), u"Command %s build error"%command.__class__.__name__
        assert command.is_coroutine_obj is not None, u"Command %s build error"%command.__class__.__name__

        if self.is_coroutine_obj is None:
            self.is_coroutine_obj = command.is_coroutine_obj
            self.commands.append(command)

            #make execute
            if self.is_coroutine_obj is False:
                self.execute = functools.partial(make_cc_execute_sync(),self)
            elif self.is_coroutine_obj is True:
                self.execute = functools.partial(make_cc_execute_async(), self)

        elif self.is_coroutine_obj is True :
            self.commands.append(command)
        elif self.is_coroutine_obj == command.is_coroutine_obj:
            self.add_command(command)
        else:
            raise ArgsError("method execute of class %s  can't invode coroutine execute of class %s")%(
                self.__class__.__name__, command.__class__.__name__
            )


    def remove_command(self, command):
        """
        删除命令
        :param command:
        :return:
        """
        self.commands.remove(command)

    

