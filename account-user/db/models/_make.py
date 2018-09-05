#-*- encoding:utf-8 -*-

__all__ = ["Model", "NOTHING", "Field"]

import logging
from functools import total_ordering
import inspect
import copy
from collections import Iterator, Iterable

from .base import ModelRelatedEntity, MetaManager
from .error import *


class _NothingBuilder(type):
    def __new__(cls, name, bases, attrs):
        if bases:
            raise NothingClassNotAllowdExtend("class %s CAN'T extend _Nothing"%name)
        return super().__new__(cls, name, bases, attrs)

    def __call__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            cls._instance = super().__call__(*args, **kwargs)
        return cls._instance


class _Nothing(metaclass=_NothingBuilder):

    def __copy__(self):
        return self

    def __deepcopy__(self, _):
        return self

    def __eq__(self, other):
        return other.__class__ == _Nothing

    def __ne__(self, other):
        return not self == other

    def __repr__(self):
        return "NOTHING"

    def __hash__(self):
        return 0xdeadbeef


NOTHING = _Nothing()

def yield_fields_from_cls(cls):
    """
    获取父类属性
    :param cls:
    :param ignore_dunder:
    :return:
    """
    for attr_name in dir(cls):
        cls_attr = getattr(cls, attr_name, None)
        if isinstance(cls_attr, Field):
            if "__" in attr_name:
                raise FieldNammingError("%s.%s" % (cls.__name__, attr_name))
            elif attr_name.lower() == "pk":
                raise FieldNammingError("%s.%s" % (cls.__name__, attr_name))
            yield attr_name, cls_attr


def yield_options_from_meta(cls_meta):
    """
    获取meta配置
    :param cls:
    :return:
    """
    #cls_meta = getattr(cls, "Meta", None)

    if inspect.isclass(cls_meta):

        for key in filter(lambda x: not \
                (x.startswith("_" or "__" in x)), dir(cls_meta)):
            yield key, getattr(cls_meta, key)


def make_model_repr():
    def __repr__(self):
        fields_info = ",".join([field.name for field in self.__class__.get_fields()])
        return "<OBJECT %s.%s %s [%s]>" % (self.__class__.__module__,
                                           self.__class__.__name__,
                                           id(self),
                                           fields_info)
    return __repr__

def assert_same_model(self, other):
    """
    断言==》是否同一个model
    :param self:
    :param other:
    :return:
    """
    assert self.__class__ is other.__class__, \
        u"type not same, %s cmp to %s" % (self.__class__, other.__class__)

def make_model_eq():
    """
    比较 ==
    :return:
    """
    def __eq__(self, other):
        assert_same_model(self, other)
        _cls = self.__class__
        return getattr(self, _cls.pk.name, None) == getattr(other, _cls.pk.name, None)

    return __eq__

def make_model_lt():
    """
    比较 <
    :return:
    """
    def __lt__(self, other):
        assert_same_model(self, other)
        _cls = self.__class__
        return getattr(self, _cls.pk.name, None) < getattr(other, _cls.pk.name, None)
    return __lt__


def make_model_fomat():
    def __format__(self):
        pass

    return __format__

def make_field_format():
    def __format__(self):
        pass

    return __format__

def make_field_set():
    def __set__(self, instance, value):
        if isinstance(instance, type):
            raise AttributeSettingError("NOT ALLOW CLASS")
        elif not self.model:
            raise AttributeSettingError("model had not set yet")
        elif not isinstance(instance, self.model):
            raise ArgsError("SOME THING WRONG")
        instance.__dict__[self.name] = value

    return __set__

def make_field_get():
    def __get__(self,instance, owner):
        if instance:
            if self.name in instance.__dict__:
                return instance.__dict__[self.name]
            else:
                raise AttributeNotExistError("object <%s %s>'s %s have not set"%(instance.__class__, instance, self.name))
        return self
    return __get__

def make_field_repr():
    def __repr__(self):
        attrs = ["name", "verbose_name", "primary_key", "unique", "db_column"]
        attrs = ["%s:%s" % (attr, getattr(self, attr, None)) for attr in attrs]
        return "<%s %s>" % (self.__class__.__name__, ",".join(attrs))
    return __repr__

def make_field_eq():
    def __eq__(self):
        pass

    return __eq__


def make_field_copy():
    def __copy__(self):
        if "model" in self.__dict__ :
            raise BuildingModelError("Field %s had tied to model %s"%(self.name, self.model.__name__))
        new_obj = self.__class__()
        new_obj.__dict__ = copy.copy(self.__dict__)
        return new_obj
    return __copy__


class Options(ModelRelatedEntity):

    def __init__(self,  **kwargs):
        """
        初始化
        :param model:
        """
        self.default_table_name = None
        self.ordering = None
        self.help_text = ""

        # 所有属性
        self.fields = []
        # 父类继承的属性
        self.super_fields = []
        # 关系
        self.relateds = []
        self.set_up(**kwargs)

    def set_up(self, **kwargs):
        self.__dict__.update(kwargs)


class ModelBuilder(type):
    """
    model meta
    """
    meta_mgr = MetaManager()

    def __new__(cls, name, bases, attrs):
        super_new = super().__new__
        parents = [b for b in bases if isinstance(b, ModelBuilder)]
        if not parents:
            return super_new(cls, name, bases, attrs)

        #不存在多个model继承
        if len(parents) > 1:
            raise BuildingModelError("[%s] are Model, Model can't extend Model, user minix style to resove it"%",".join([p.__name__ for p in parents]))

        # new_class
        _meta_dict = {}
        _meta = attrs.pop("Meta", None)
        if _meta:
            for key, value in yield_options_from_meta(_meta):
                _meta_dict[key] = value

        if "default_table_name" not in _meta_dict:
            _meta_dict["default_table_name"] = name.lower()

        super_fields = {}
        for base in bases[::-1]:
            for (attr_name, attr) in yield_fields_from_cls(base):
                new_attr = copy.deepcopy(attr)
                super_fields[attr_name] = new_attr

        local_fields = {}
        _meta_dict.update(super_fields=super_fields.values())
        other_model_relateds = []

        for key in list(attrs.keys()):
            if key == "_meta":
                raise BuildingModelError("`_meta` is keyword, use other instead ")
            if isinstance(attrs[key], Field):
                if "__" in key:
                    raise FieldNammingError("%s:%s" % (name, key))
                elif key.lower() == "pk":
                    raise FieldNammingError("%s:%s" % (name, key))
                local_fields[key] = attrs.pop(key)
            elif isinstance(attrs[key], ModelRelatedEntity):
                other_model_relateds.append((key, attrs[key]))
                attrs.pop(key)

        super_fields.update(local_fields)
        if len(super_fields) == 0:
            raise BuildingModelError("Model was not allowed that has no field. nameed %s"%name)
        _meta_dict.update(fields=super_fields.values())



        options = Options(**_meta_dict)
        if "__repr__" not in attrs:
            attrs["__repr__"] = make_model_repr()
        if "__str__" not in attrs:
            attrs["__str__"] = attrs["__repr__"]

        #cmp
        attrs["__eq__"] = make_model_eq()
        attrs["__lt__"] = make_model_lt()

        new_cls = super_new(cls, name, bases, attrs)
        new_cls = total_ordering(new_cls)
        new_cls.register(ModelBuilder.meta_mgr)


        new_cls.add_to_model("_meta", options)
        for name, field in super_fields.items():
            new_cls.add_to_model(name, field)

        #其他model related
        for name, item in other_model_relateds:
            new_cls.add_to_model(name, item)

        #判断是否有pk
        if not hasattr(new_cls, "pk"):
            raise BuildingModelError("Model %s was not allows has no pk ."%name)
        return new_cls


class FieldBuilder(type):
    """
    属性建构起
    """
    def __new__(cls, name, bases, attrs):

        super_new = super().__new__
        parents = [p for p in bases if isinstance(p, FieldBuilder)]

        if "__repr__" not in attrs:
            attrs["__repr__"] = make_field_repr()

        if "__str__" not in attrs:
            attrs["__str__"] = attrs["__repr__"]

        if "__get__" not in attrs:
            attrs["__get__"] = make_field_get()

        if "__set__" not in attrs:
            attrs["__set__"] = make_field_set()

        attrs["__copy__"] = attrs["__deepcopy__"] = make_field_copy()

        new_cls = super_new(cls, name, bases, attrs)
        return new_cls

def func_wraper(func):
    """
    方法转化
    :param func:
    :return:
    """
    func_sign = inspect.signature(func)
    param_len = len(func_sign.parameters)
    assert  param_len <= 2, u"func parameter's number less than 2"
    if param_len == 0:
        return lambda instance, x: func()
    elif param_len == 1 and "self" in func_sign.parameters:
        return lambda instance, x: func(instance)
    elif param_len == 2:
        return func
    else:
        return lambda instance, x: func(x)


class _Processor(object):

    def __init__(self, func=None):
        self._processor = None
        if not func:
            self.add_processor(func)

    def add_processor(self, func):
        raise  NotImplemented

    def __call__(self, value, instance):
        raise NotImplemented

    @property
    def processor(self):
        return self._processor

    def func_can_add(self, func):
        return not isinstance(func, _Processor)



class _Converter(_Processor):
    """
    数据转换器
    """

    def _init__(self, func=None):
        super().__init__()

    def add_processor(self, func):
        if not self.func_can_add(func):
            raise ArgsError("_Processor object is not allowed set as %s"%self.__class__)
        elif self.processor is not None:
            raise ArgsError("%s object has set"%self.__class__)
        elif callable(func):
            self._processor = func_wraper(func)

    def __call__(self, value, instance):

        if self._processor:
           return self._processor(instance, value)
        return value


class _Defaultor(_Converter):
    """
    数据默认
    """

    def __init__(self, func=None):
        self._default = NOTHING
        self._processor = None
        if not callable(func):
            self._default = func
        else:
            self.add_processor(func)


    def add_processor(self, func):
        if self._default is not NOTHING:
            raise ArgsError("default had set. value is %s"%self._default)
        super().add_processor(func)

    def __call__(self, instance=None, other=None):
        _value = NOTHING
        if self._default is not NOTHING:
            _value = self._default
        elif self._processor:
            _value = self._processor(instance, other)

        return _value


class _Validator(_Processor):
    """
    数值检验
    """

    def __init__(self, func=None):
        self._processor = []
        if not func:
            self.add_processor(func)


    def add_processor(self, funcs):
        if not self.func_can_add(funcs):
            raise ArgsError("_Validator object is not allowed set as _Processor")

        elif isinstance(funcs, (Iterable, Iterator)):
            for func in funcs:
                self.add_processor(func)

        elif callable(funcs):
            self._processor.append(func_wraper(funcs))

    def __call__(self, value, instance=None):
        """
        :param value:
        :return:
        """
        if not self._processor:
            return value

        for processor in self._processor:
            print("process's :%s"%processor.__dict__)
            processor(instance, value)


        return value


    def __repr__(self):
        return "<class %s:%s>"%(self.__class__.__name__, self)

    def __str__(self):
        return "<%s, %s,%s,%s>"%(id(self), self.multiable, len(self._processors), len(self.ref_set))



class Field(ModelRelatedEntity, metaclass=FieldBuilder):
    """
    属性
    """
    def __init__(self, verbose_name=None, primary_key=False,
                 max_length=None, unique=False, null=False, default=NOTHING,
                 help_text='', db_column=None, validator=None, converter=None
                 ):

        self.verbose_name = verbose_name
        self.primary_key = primary_key
        self.max_length = max_length
        self.unique = unique
        self.null = null
        self.help_text = help_text
        self.db_column = db_column

        self._default = _Defaultor(default)
        self._validators = _Validator(validator)
        self._converter = _Converter(converter)


    def validator(self, func):
        """
        检验器
        :param func:
        :return:
        """
        self._validators.add_processor(func)

    def converter(self, func):
        """
        数据转换器
        :param func:
        :return:
        """
        self._converter.add_processor(func)

    def default(self, func):
        """
        数据默认值
        :param func:
        :return:
        """
        self._default.add_processor(func)

    def contribute_to_modelx(self, model, name):
        if self.primary_key:
            model.set_pk(self)

    def validate(self, value, instance=None):
        """
        数据校验处理
        :param value:
        :param instance:
        :return:
        """
        self._validators(value, instance)

    def convert(self, value, instance=None):
        """
        数据转换处理
        :param value:
        :param instance:
        :return:
        """
        value = self._converter(value, instance)
        #更新
        if getattr(instance, "__dict__"):
            instance.__dict__[self.name] = value

    def get_default(self, instance=None):
        """
        默认值
        :param instance:
        :return:
        """
        return self._default(instance)

    @property
    def column_name(self):
        return self.db_column or self.name


class cache_property(object):

    def __init__(self, func, name=None):
        self._func = func
        self._property_name = name if name else func.__name__
        self.__doc__ = func.__doc__

    def __set__(self, instance, value):
        instance.__dict__[self._property_name] = value


    def __get__(self, instance, owner=None):
        return self._func(instance)



class Model(metaclass=ModelBuilder):

    def __init__(self, *args, **kwargs):

        for (k, v) in kwargs.items():
            _field = getattr(self.__class__, k, None)
            if isinstance(_field, Field):
                setattr(self, k, v)


    @classmethod
    def get_fields(cls):
        return cls._meta.fields

    @classmethod
    def register(cls, meta_mgr):
        if hasattr(cls, "_meta_mgr"):
            raise BuildingModelError("meta manager had registed")
        cls._meta_mgr = meta_mgr
        meta_mgr.add_meta(cls)

    @classmethod
    def add_to_model(cls, attr_name, attr_value):
        if hasattr(attr_value, "contribute_to_model"):
            attr_value.contribute_to_model(cls, attr_name)
        setattr(cls, attr_name, attr_value)


    @classmethod
    def set_pk(cls, field):
        if not isinstance(field, Field) :
            raise ArgsError("field must extend Field")
        elif field.__class__ is Field:
            raise ArgsError("field must extend Field, but not Field")

        pk = getattr(cls, "pk", None)
        if pk:
            raise BuildingModelError("model %s had pk: %s"%(cls.__name__, getattr(pk, "name", "")))

        setattr(cls, "pk", field)

    @classmethod
    def assert_is_model(cls):
        assert issubclass(cls, Model), u"cls %s is not a model" % cls.__name__

    @classmethod
    def get_field_names(cls):
        #cls.assert_is_model()
        if not hasattr(cls._meta, "field_names"):
            for field in cls.get_fields():
                yield field.name

    @classmethod
    def get_table_name(cls):
        #cls.assert_is_model()
        return cls._meta.default_table_name


    @classmethod
    def get_column_names(cls):
        #cls.assert_is_model()
        for field in cls.get_fields():
            yield field.column_name or field.name


    def clean(self):
        for field in self._meta.fields:
            #先转换
            if field.name in self.__dict__:
                field._converter(self.__dict__[field.name], self)
                _value = self.__dict__.get(field.name)
                field._validators(_value, self)


    def diff(self, other):
        """
        两个对象比较
        :param other:
        :return:
        """
        assert_same_model(self, other)

        if self == other:
            _diff = {}
            for field in self._meta.fields:
                value, value1 = getattr(self, field.name, None), getattr(other, field.name, None)
                if field.primary_key:
                    _diff[field.name] = value

                elif value != value1:
                    _diff[field.name] = value1

            return 1, self.__class__(**_diff)
        else:
            return 0, other

    @property
    def PK(self):
        attr_name = self.__class__.pk.name
        if not attr_name in self.__dict__:
            return self.__class__.pk.get_default(self)
        return self.__dict__[attr_name]


    def as_dict(self, ignore=None, **extra):
        _cls = self.__class__
        ignore_keys = []
        if isinstance(ignore, str):
            ignore_keys.append(ignore)
        elif isinstance(ignore, (Iterable, Iterator)):
            ignore_keys.extend(ignore)

        data = dict(self.as_tuple())
        if ignore_keys:
            for key in ignore_keys:
                data.pop(key, None)

        extra.update(data)
        return data

    def as_tuple(self, raise_error=False):
        cls = self.__class__
        for field in cls._meta.fields:
            if field.name in self.__dict__:
                _value = self.__dict__[field.name]
                if _value is NOTHING:
                    self.__dict__.pop(field.name)
            else:
                _value = field.get_default(self)

            if  raise_error and _value is NOTHING:
                raise AttributeSettingError("field %s in model %s had not set yet" % (field.name, cls.__name__))

            yield field.name, _value


    def field_values(self):
        for field_name, field_value in self.as_tuple():
            yield field_value


if __name__ == "__main__":
    print(isinstance(Model, ModelBuilder))
    print()

