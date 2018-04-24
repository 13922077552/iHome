# -*- coding: utf-8 -*-
# 房屋模块
from flask import current_app, jsonify, request, g, session
from iHome.models import Area, House, Facility, HouseImage
from iHome.utils.response_code import RET
from . import api
from iHome.utils.common import login_required
from iHome import db, constants, redis_store
from iHome.utils.image_storage import upload_image


@api.route('/houses/index', methods=['GET'])
def get_houses_index():
    """⾸⻚房屋推荐接⼝
    1.查询最新发布的五个房屋信息
    2.构造响应数据
    3.响应结果
    """
    # 1.查询最新发布的五个房屋信息
    try:
        houses = House.query.order_by(House.create_time.desc()).limit(constants.HOUSE_LIST_PAGE_CAPACITY)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查询房屋数据失败")

    # 2.构造响应数据
    house_dict_list = []
    for house in houses:
        house_dict_list.append(house.to_basic_dict())

    # 3.响应结果
    return jsonify(errno=RET.OK, errmsg="OK", data=house_dict_list)


@api.route('/houses/<house_id>', methods=['GET'])
def get_house_detail(house_id):
    """提供房屋详情数据
    1.直接查询house_id对应的房屋信息
    2.构造房屋详情数据
    3.响应房屋详情数据
    """
    # 1.直接查询house_id对应的房屋信息
    try:
        house = House.query.get(house_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询房屋数据失败')
    if not house:
        return jsonify(errno=RET.NODATA, errmsg='房屋不存在')

    # 2.构造房屋详情数据
    response_house_detail = house.to_full_dict()

    # 尝试获取登录用户的信息：有可能未登录
    longin_user_id = session.get('user_id', -1)

    # 3.响应房屋详情数据
    return jsonify(errno=RET.OK, errmsg='OK', data=response_house_detail, login_user_id=longin_user_id)


@api.route('/houses/image', methods=['POST'])
@login_required
def upload_house_image():
    """上传房屋图片
    0.判断是否登录
    1.接受参数，image_data,house_id
    2.使用house_id，查询房屋信息，只有当房屋存在时，才会上传图片
    3.调用上传图片的工具，上传房屋的图片
    4.创建HouseImage模型对象，并保存房屋图片key，保存到数据库
    5.响应结果
    """
    # 1.接受参数，image_data,house_id
    try:
        image_data = request.files.get('house_image')
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="图⽚有误")
    house_id = request.form.get('house_id')
    if not house_id:
        return jsonify(errno=RET.PARAMERR, errmsg="缺少必传参数")
    # 获取房屋模型对象
    # 2.使用house_id，查询房屋信息，只有当房屋存在时，才会上传图片
    try:
        house = House.query.get(house_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询房屋数据失败')
    if not house:
        return jsonify(errno=RET.NODATA, errmsg='房屋不存在')

    # 3.调用上传图片的工具，上传房屋的图片
    try:
        key = upload_image(image_data)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR, errmsg='上传图⽚失败')

    # 4.创建HouseImage模型对象，并保存房屋图片key，保存到数据库
    house_image = HouseImage()
    house_image.house_id = house_id
    house_image.url = key

    # 给房屋设置默认的图片
    if not house.index_image_url:
        house.index_image_url = key

    try:
        db.session.add(house_image)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg='保存房屋图⽚数据失败')

    # 5.响应结果
    house_image_url = constants.QINIU_DOMIN_PREFIX + key
    return jsonify(errno=RET.OK, errmsg='上传房屋图⽚成功', data={'house_image_url': house_image_url})


@api.route('/houses', methods=['POST'])
@login_required
def pub_house():
    """发布房源
    0.判断用户是否登录
    1.接受参数，基本信息个设备信息
    2.判断参数是否为空，并对某些参数进行合法性的校验，比如个金钱相关的
    3.创建房屋模型对象，并赋值
    4.保存房屋数据到数据库
    5.响应发布新的房源的结果
    """
    # 1.接受参数，基本信息个设备信息
    json_dict = request.json
    title = json_dict.get('title')
    price = json_dict.get('price')
    address = json_dict.get('address')
    area_id = json_dict.get('area_id')
    room_count = json_dict.get('room_count')
    acreage = json_dict.get('acreage')
    unit = json_dict.get('unit')
    capacity = json_dict.get('capacity')
    beds = json_dict.get('beds')
    deposit = json_dict.get('deposit')
    min_days = json_dict.get('min_days')
    max_days = json_dict.get('max_days')
    facility = json_dict.get('facility')  # [2,4,6,8,10]

    # 2.判断参数是否为空，并对某些参数进行合法性的校验，比如个金钱相关的
    if not all([title, price, address, area_id, room_count, acreage, unit, capacity, beds, deposit, min_days, max_days,
                facility]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数缺失')

    # 校验价格格式并转成以分的形式保存,
    try:
        price = int(float(price) * 100)
        deposit = int(float(deposit) * 100)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="参数格式错误")

    # 3.创建房屋模型对象，并赋值
    house = House()
    house.user_id = g.user_id
    house.area_id = area_id
    house.title = title
    house.price = price
    house.address = address
    house.room_count = room_count
    house.acreage = acreage
    house.unit = unit
    house.capacity = capacity
    house.beds = beds
    house.deposit = deposit
    house.min_days = min_days
    house.max_days = max_days

    # 给facilities属性赋值，实现多对多的关联关系 facility == [2,4,6,8,10]
    facility = Facility.query.filter(Facility.id.in_(facility)).all()
    house.facilities = facility

    # 4.保存房屋数据到数据库
    try:
        db.session.add(house)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="保存房屋数据失败")

    # 5.响应发布新的房源的结果
    return jsonify(errno=RET.OK, errmsg="发布新房源成功", data={'house_id':house.id})


@api.route('/areas', methods=['GET'])
def get_areas():
    """提供城区的信息
    1.直接查询所有城区信息
    2.构造城区信息响应数据
    3.响应城区信息
    """
    # 先从缓存中去取，如果缓存中没有，再去数据库中取
    try:
        area_dict_list = redis_store.get('Areas')
        # 如果缓存的城区数据存在，就转成字典列表响应出去
        if area_dict_list:
            return jsonify(errno=RET.OK, errmsg="OK",data=eval(area_dict_list))
    except Exception as e:
        current_app.logger.error(e)

    # 1.直接查询所有城区信息areas == [Area, Area, Area]
    try:
        areas = Area.query.all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查询地区数据失败")

    # 2.构造城区信息响应数据
    area_dict_list = []
    for area in areas:
        area_dict_list.append(area.to_dict())

    # 缓存城区数据，set：储存
    try:
        redis_store.set('Areas', area_dict_list,constants.AREA_INFO_REDIS_EXPIRES)
    except Exception as e:
        current_app.logger.error(e)

    # 3.响应城区信息
    return jsonify(errno=RET.OK, data=area_dict_list)
