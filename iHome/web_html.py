# -*- coding: utf-8 -*-
from flask import Blueprint, current_app, make_response
from flask_wtf.csrf import generate_csrf

html_blue = Blueprint('web_html', __name__)


# 静态⽂件全路径：static/html/register.html
@html_blue.route('/<re(".*"):file_name>')
def get_html_file(file_name):
    """自定义获取静态html的方式"""
    if not file_name:
        # 自定义一个跟路径为空也能匹配师徒的规则
        # 当没有输入地址的时候，file_namewe空的时候访问首页
        file_name = 'index.html'
    if file_name != 'favicon.ico':
        # 静态⽂件全路径：static/html/register.html
        file_name = 'html/' + file_name

    # 创建响应对象
    response = make_response(current_app.send_static_file(file_name))
    # 生成csrf_token
    csrf_token = generate_csrf()
    # 将csrf_roken写入到cookie
    response.set_cookie('csrf_token', csrf_token)

    # 默认去static文件夹去找，所有不用/static
    return response
