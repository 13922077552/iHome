# -*- coding: utf-8 -*-
from . import api
from iHome.utils.common import login_required
from flask import g, request, jsonify, current_app, session
from iHome.utils.response_code import RET
import datetime
from iHome.models import House, Order, User
from iHome import db


@api.route('/orders/<int:order_id>', methods=['PUT'])
@login_required
def set_order_status(order_id):
    """接受订单
    0.判断是否登录
    1.获取order_id,并查询订单,状态要是"待接单"
    2.判断当前登录用户是否是该订单的房东
    3.修改订单状态，并保存到数据库
    4.响应请求
    """

    user_id = g.user_id
    # 1.获取order_id,并查询订单,状态要是"待接单"
    try:
        order = Order.query.filter(Order.id==order_id, Order.status == 'WAIT_ACCEPT').all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查询数据失败")
    if not order:
        return jsonify(errno=RET.NODATA, errmsg="订单不存在")

    # # 2.判断当前登录用户是否是该订单的房东
    order_user_id = order.user_id
    if order_user_id != user_id:
        return jsonify(errno=RET.ROLEERR, errmsg="用户身份错误")
    # 3.修改订单状态，并保存到数据库
    order.status = 'WAIT_COMMENT'
    try:
        db.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="修改订单信息失败")

    # 响应数据
    return jsonify(errno=RET.OK, errmsg="OK")


@api.route('/orders', methods=['GET'])
@login_required
def get_order_list():
    """获取我的订单和客户订单
    0.判断是否登录
    1.获取用户id
    3.查找数据库
    4.响应数据
    """
    # 获取当前用户的id
    user_id = g.user_id
    role = request.args.get('role')
    # 查找数据库
    # 查找我的订单列表
    if role not in ['custom', 'landlord']:
        return jsonify(errno=RET.PARAMERR, errmsg='⽤户身份信息错误')
    if role == 'custom':
        try:
            orders = Order.query.filter(Order.user_id == user_id).all()
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR, errmsg="查询订单数据失败")
    else:
        # 查找客户订单
        try:
            user = User.query.get(user_id)
            orders = Order.query.filter(Order.house_id.in_([house.id for house in user.houses]))
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR, errmsg="查询订单数据失败")

    order_dict_list = []
    if orders:
        for order in orders:
            order_dict_list.append(order.to_dict())
    return jsonify(errno=RET.OK, errmsg="OK", data=order_dict_list)


@api.route('/orders', methods=['POST'])
@login_required
def add_order():
    """添加订单
    0.判断是否登录
    1.接收参数，房屋id，用户id
    2.校验参数
    3.计算入住天数
    4.判断房屋是否存在
    5.判断房屋是否是当前登录用户的
    6.查询是否存在冲突的订单
    7.生成订单模型，提交订单
    8.响应请求
    """

    # 1 判断是否登录
    # 2 接收参数，房屋id，用户id
    # 获取当前用户的id
    user_id = g.user_id
    # 获取传入的参数
    params = request.json
    start_date_str = params.get('start_date')
    end_date_str = params.get('end_date')
    house_id = params.get('house_id')
    # 3 校验参数
    if not all([start_date_str, end_date_str, house_id]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不能为空")
    try:
        start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d')
        end_date = datetime.datetime.strptime(end_date_str, '%Y-%m-%d')
        assert start_date < end_date, Exception('开始日期大于结束日期')
        # 4 计算入住天数
        days = (end_date - start_date).days
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="⼊住时间有误")

    # 5 判断房屋是否存在
    try:
        house = House.query.get(house_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查询房屋数据失败")
    if not house:
        return jsonify(errno=RET.NODATA, errmsg="房屋不存在")

    # 6 判断房屋是否是当前登录用户的
    if user_id == house.user_id:
        return jsonify(errno=RET.ROLEERR, errmsg="不能预定自己的房屋哦")

    # 7 查询是否存在冲突的订单
    try:
        conflict_orders = Order.query.filter(Order.house_id == house_id, end_date > Order.begin_date,
                                             start_date < Order.end_date).all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查询冲突订单失败")
    if conflict_orders:
        return jsonify(errno=RET.DATAERR, errmsg="该房屋已被预订")

    # 8 生成订单模型，提交订单
    order = Order()
    order.user_id = user_id  # 下订单的用户编号
    order.house_id = house_id  # 预订的房间编号
    order.begin_date = start_date  # 预订的起始时间
    order.end_date = end_date  # 预订的结束时间
    order.days = days  # 预订的总天数
    order.house_price = house.price  # 房屋的单价
    order.amount = house.price * days  # 订单的总金额

    try:
        db.session.add(order)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DATAERR, errmsg="保存订单数据到数据库失败")

    # 9 响应请求
    return jsonify(errno=RET.OK, errmsg="OK")
