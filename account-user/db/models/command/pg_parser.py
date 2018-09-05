#-*- encoding:utf-8 -*-

__author__ = "474416133@qq.com"

import inspect

from collections import Iterable

from db.models.error import *
from db.models._make import NOTHING, Model

def parse_for_insert(obj, fields=None):
    """
    转化为insert语句
    :param obj:
    :param fields:
    :return:
    """
    column_names, values_holder, values = "", "", []
    cls = obj.__class__
    for _index, t in enumerate(obj.as_tuple(raise_error=True)):
        field_name, field_value = t
        field = getattr(cls, field_name, None)
        if not field:
            raise BuildingModelError("%s has loss from Model when build." % (field_name, cls.__name__))
        column_names += ", %s" % (field.column_name)
        values_holder += ", ${}".format(_index + 1)
        values.append(field_value)

    column_names, values_holder = column_names[1:], values_holder[1:]
    sql = "INSERT INTO {table_name} ({column_names}) VALUES ({value_holders})".format(
        table_name=cls.get_table_name(),
        column_names=column_names,
        value_holders=values_holder)
    return sql, values


def parse_for_update(obj, fields=None):
    """
    转化为更新语句
    :param obj:
    :param fields:
    :return:
    """

    if fields and not isinstance(fields, Iterable):
        raise ArgsError("fields must be a iterable object")

    field_set = set(fields)

    update_columns, values = "", []

    cls = obj.__class__
    field_names = fields or list(cls.get_field_names())
    # 删除pk
    field_set.pop(cls.pk.name)
    holder_count = 1
    for field_name, field_value in obj.as_tuple(raise_error=True):

        if field_name in field_set:
            field = getattr(cls, field_name)
            if not field:
                raise BuildingModelError("field %s lost in running" % field_name)
            update_columns += ", {} = ${}".format(field.column_name, holder_count)
            holder_count += 1
            values.append(field_value)

    update_columns = update_columns[1:]
    values.append(obj.__dict__[cls.pk.name])
    sql = "UPDATE {table_name} SET {update_fields} WHERE {where}".format(
        table_name=cls.get_table_name(),
        update_fields=update_columns,
        where="{pk} = ${holder_count}".format(pk=cls.pk.column_name, holder_count=holder_count))
    return sql, values


def parse_for_delete(obj, fields=None):
    """
    转化为删除语句
    :param obj:
    :param fields:
    :return:
    """
    if inspect.isclass(obj) and issubclass(obj, Model):
        return "DELETE FROM {table_name} ".format(
            table_name=obj.get_table_name(),

        ), None
    elif isinstance(obj, Model):
        cls = obj.__class__
        if cls.pk.name in cls:
            return "DELETE FROM {table_name} WHERE {pk} = $1".format(
                table_name=cls.get_table_name(),
                pk=cls.pk.column_name
            ), [obj.__dict__[cls.pk.name]]
        else:
            sql = "DELETE FROM {table_name}".format(table_name=cls.table_name)
            countor = 1

            values = []
            for key, value in obj.as_tuple():
                field = getattr(cls, key)
                column_name = field.column_name or field.name
                if not field:
                    continue
                if value is NOTHING:
                    continue
                if countor == 1:
                    sql += " WHERE %s = $%s " % (column_name, countor)
                else:
                    sql += " AND %s = $%s " % (column_name, countor)

                values.append(values)
                countor += 1
            return sql, values
    else:
        raise ArgsError("a model or model object")


def parse_for_insertmany(obj, fields=None):
    """
    批量插入
    :param obj:
    :param fields:
    :return:
    """
    if isinstance(obj, Iterable):
        sql, values = None, []
        has_format = False
        for item in obj:

            if not has_format:
                sql, _values = parse_for_insert(item)
                values.append(_values)
                has_format = True

            else:
                values.append([v for k, v in item.as_tuple(True)])

        return sql, values

    else:
        cls = getattr(obj, "__class__", None)
        if cls and hasattr(cls, "_meta"):
            return parse_for_insert()(obj)
        raise ArgsError("arg obj not a usable obj")


def parse_for_get(obj, fields=None):
    """
    转化为查询语句
    :param obj:
    :param fields:
    :return:
    """
    pass


def parse_for_count(sql, params):
    """
    计数
    :param sql:
    :param params:
    :return:
    """
    return sql, params