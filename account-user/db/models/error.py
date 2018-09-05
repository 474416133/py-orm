#-*- encoding:utf-8 -*-

__author__ = "474416133@qq.com"

__all__ = ["FieldNammingError", "BuildingModelError", "AttributeSettingError",
           "DuplicateKeyError", "ArgsError", "AttributeNotExistError", "NothingClassNotAllowdExtend",
           "NoBindingModelError", "ModelNotMatchError", "QueryOpError"]

ERROR_MSG_SPLITE = ":"

class ErrorMinix(object):
    err_msg = ""
    def __init__(self, msg):
        self.err_msg = ERROR_MSG_SPLITE.join((self.err_msg, msg))

    def __repr__(self):
        return '<%s>%s' % (self.__class__.__name__, self.err_msg)

    def __str__(self):
        return "cause %s:%s" % (self.__class__.__name__, self.err_msg)

class FieldNammingError(AttributeError, ErrorMinix):
    err_msg = "fields namming can't not contain double underline or is `pk`"


class BuildingModelError(RuntimeError, ErrorMinix):
    err_msg = "cause error where building new model"

class AttributeSettingError(AttributeError, ErrorMinix):
    err_msg = "attribute setting error"

class DuplicateKeyError(KeyError, ErrorMinix):
    err_msg = "key has exist"

class ArgsError(RuntimeError, ErrorMinix):
    err_msg = "define error"

class AttributeNotExistError(AttributeError, ErrorMinix):
    err_msg = "attribute setting error"


class NothingClassNotAllowdExtend(RuntimeError, ErrorMinix):
    """
    NOthing 不允许继承
    """
    err_msg = "NOthing class NOT ALLOW to extend"

class NoBindingModelError(RuntimeError, ErrorMinix):
    """
    模型未绑定
    """
    err_msg = "NoBindingModel error"

class ModelNotMatchError(RuntimeError, ErrorMinix):
    """
    模型不匹配
    """
    err_msg = "ModelNotMatchError"

class QueryOpError(RuntimeError, ErrorMinix):
    """
    query操作错误
    """
    err_msg = "QueryOpError"

