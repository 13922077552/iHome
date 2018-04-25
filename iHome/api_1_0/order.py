# -*- coding: utf-8 -*-
from . import api
from iHome.utils.common import login_required
from flask import g, request, jsonify, current_app, session
from iHome.utils.response_code import RET
import datetime
from iHome.models import House, Order
from iHome import db

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
    start_date_str = params.get('house_id')
    end_date_str = params.get('end_date')
    house_id = params.get('house_id')
    # 3 校验参数
    if not all([start_date_str, end_date_str, house_id]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不能为空")
    try:
        start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%s')
        end_date = datetime.datetime.strptime(end_date_str, '%Y-%m-%s')
        assert start_date < end_date, Exception('开始日期大于结束日期')
        # 4 计算入住天数
        days = end_date - start_date
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
        conflict_orders = Order.query.filter(Order.house_id==house_id, end_date>Order.begin_date, start_date<Order.end_date )
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