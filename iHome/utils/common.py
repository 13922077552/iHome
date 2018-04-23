# -*- coding: utf-8 -*-
from flask import g
from werkzeug.routing import BaseConverter
from flask import session, jsonify
from iHome.utils.response_code import RET
from functools import wraps


class RegexConverter(BaseConverter):
    """自定义路由转换器"""

    def __init__(self, url_map, *args):
        super(RegexConverter, self).__init__(url_map)
        self.regex = args[0]


def login_required(func):
    """自定义装饰器判断用户是否登录
        使用装饰器装饰函数，会修改被装饰函数的__name__属性和被装饰的函数的说明文档
        为了不让装饰器影响被装饰的函数的默认的数据，我们会使用@wraps装饰器，提前对view_fun进行装饰
    """

    @wraps(func)
    def wraaper(*args, **kwargs):
        """具体实现判断用户是否登录的逻辑"""
        user_id = session.get('user_id')
        if not user_id:
            return jsonify(errno=RET.SESSIONERR, errmsg="用户未登录")
        else:
            g.user_id = user_id
            return func(*args, **kwargs)

    return wraaper
