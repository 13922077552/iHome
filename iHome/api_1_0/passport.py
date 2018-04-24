# -*- coding: utf-8 -*-
# 登录注册

from . import api
from flask import request, jsonify, current_app, session
import json, re
from iHome.utils.response_code import RET
from iHome import redis_store, db
from iHome.models import User
from iHome.utils.common import login_required


@api.route('/sessions', methods=['GET'])
def chesk_login():
    """判断用户是否登录
    1.获取session信息
    2.
    """
    user_id = session.get('user_id')
    name = session.get('name')
    return jsonify(errno=RET.OK, errmsg="OK", data={'user_id': user_id, 'name': name})


@api.route('/sessions', methods=['DELETE'])
@login_required
def logout():
    """实现退出登录逻辑
    0.判断用户是否登录
    1.清理session数据
    """
    session.pop('user_id')
    session.pop('name')
    session.pop('mobile')

    return jsonify(errno=RET.OK, errmsg="退出登录成功")


@api.route('/sessions', methods=['POST'])
def login():
    """登录
    1.接受登录参数：手机号码，密码明文
    2.校验参数：是否缺少参数，是否合法
    3.使用手机号查询用户，并判断是否存在
    4.校验用户名密码是否正确
    5.写入状态保持信息到session中
    6.响应登录结果
    """
    # 1.接受登录参数：手机号码，密码明文
    json_dict = request.json
    mobile = json_dict.get('mobile')
    password = json_dict.get('password')

    # 2.校验参数：是否缺少参数，是否合法
    if not all([mobile, password]):
        return jsonify(errno=RET.PARAMERR, errmsg="缺少参数")
    if not re.match(r'^1[34578][0-9]{9}$', mobile):
        return jsonify(errno=RET.PARAMERR, errmsg="手机号码格式不正确")

    # 3.使用手机号查询用户，并判断是否存在
    try:
        user = User.query.filter(User.mobile == mobile).first()
    except Exception as e:
        current_app.logger.error(e)  # logger:记录器，error错误
        return jsonify(errno=RET.DBERR, errmsg="查询用户失败")
    if not user:
        return jsonify(errno=RET.USERERR, errmsg="用户名或者密码错误")

    # 4.校验用户名密码是否正确
    if not user.check_pawword(password):
        return jsonify(errno=RET.PWDERR, errmsg="用户名或密码错误")

    # 5.写入状态保持信息到session中
    session['user_id'] = user.id
    session['name'] = user.name
    session['mobile'] = user.mobile

    # 6.响应登录结果
    return jsonify(errno=RET.OK, errmsg="登录成功")


@api.route('/users', methods=['POST'])
def register():
    """注册
    1.获取注册参数：手机号码，短信验证码，密码
    2.判断参数是否缺少
    3.获取服务器储存的短信验证码
    4.与客户端传入的短信验证码做对比
    5.如果成功，就创建用户模型User对象，并给属性赋值
    6.将模型属性写入到数据库
    7.响应注册结果
    """
    # 1.获取注册参数：手机号，短信验证码，密码
    # json_str = request.data
    # json_dict = json.loads(json_str)
    # 当我们后端确定前端发来的是json字符串时
    # json_dict = request.get_json()
    json_dict = request.json
    mobile = json_dict.get('mobile')
    sms_code_client = json_dict.get('sms_code')
    password = json_dict.get('password')

    # 2.判断参数是否缺少
    if not all([mobile, sms_code_client, password]):
        return jsonify(errno=RET.PARAMERR, errmsg='缺少参数')
    if not re.match(r'^1[345678][0-9]{9}$', mobile):
        return jsonify(errno=RET.PARAMERR, errmsg='手机号格式错误')

    # 3.获取服务器存储的短信验证码
    try:
        sms_code_server = redis_store.get('SMS:%s' % mobile)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询短信验证码失败')
    if not sms_code_server:
        return jsonify(errno=RET.NODATA, errmsg='短信验证码不存在')

    # 4.与客户端传入的短信验证码对比
    if sms_code_server != sms_code_client:
        return jsonify(errno=RET.PARAMERR, errmsg='短信验证码输入有误')

    # 判断用户是否已注册
    if User.query.filter(User.mobile == mobile).first():
        return jsonify(errno=RET.DATAEXIST, errmsg="该手机号已经注册")

    # 5.如果对比成功，就创建用户模型User对象，并给属性赋值
    user = User()
    user.mobile = mobile
    user.name = mobile  # 默认把手机号作为用户名，如果不喜欢，后面会提供修改用户名的接口

    # TODO:需要将密码加密后保存到数据库:调用password属性的setter方法
    user.password = password

    # 6.将模型属性写入到数据库
    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg='保存用户注册数据失败')

    # 注册即登录，也就是保存注册时生成的状态保持数据
    session['user_id'] = user.id
    session['name'] = user.name
    session['mobile'] = user.mobile
    # 7.响应注册结果
    return jsonify(errno=RET.OK, errmsg='注册成功')
