# -*- coding: utf-8 -*-
from flask import Blueprint

# 创建api v1.0 的蓝图  http://www.example.com/api/1.0/info
api = Blueprint('api', __name__, url_prefix='/api/1.0')
# 导入index，让@api.route('/',method=['GET','POST'])有机会执行
from . import verify, passport, profile, house, order
