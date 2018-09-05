#-*- encoding:utf-8 -*-

__author__ = "474416133@qq.com"

#import weakref

from .error import  *


class ImmutableAttribute(object):
    """
    不可变属性
    """
    def __init__(self, name):
        self.name = name

    def __get__(self, instance, owner=None):
        if instance :
            return instance.__dict__[self.name]
        elif owner:
            return self

    def __set__(self, instance, value):
        if self.name in instance.__dict__:
            raise AttributeSettingError("%s'%s:had set"%(instance, self.name))
        instance.__dict__[self.name] = value

    def __repr__(self):
        return "<ImmutableAttribute: %s>"%self.name

    __str__ = __repr__



def set_attr_immutable(maybe_cls, name):
    """
    设置对象不可变属性
    :param maybe_cls:
    :param name:
    :return:
    """
    setattr(maybe_cls, name, ImmutableAttribute(name))


class ModelRelatedEntity(object):
    """
    模型相关的对象
    """
    def contribute_to_model(self, model, name):
        self.name = name
        self.model = model
        self.contribute_to_modelx(model, name)

    def contribute_to_modelx(self, model, name):
        pass



set_attr_immutable(ModelRelatedEntity, "name")
set_attr_immutable(ModelRelatedEntity, "model")


class MetaManager(object):
    """
    模型管理器
    """

    def __init__(self):
        self.metas = {}

    def add_meta(self, meta):
        key = self._get_key(meta)
        if key in self.metas:
            raise DuplicateKeyError("%s HAD SET IN %s"%(key, self.__class__.__name__))
        self.metas[key] = meta


    def remove(self, meta):
        self.metas.pop(self._get_key(meta), None)

    def _get_key(self, meta):
        return "%s.%s"%(meta.__module__, meta.__name__)


