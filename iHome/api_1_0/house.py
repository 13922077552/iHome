# -*- coding: utf-8 -*-
# 房屋模块
from flask import current_app, jsonify
from iHome.models import Area
from iHome.utils.response_code import RET
from . import api


@api.route('/areas', methods=['GET'])
def get_areas():
    """提供城区的信息
    1.直接查询所有城区信息
    2.构造城区信息响应数据
    3.响应城区信息
    """
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

    # 3.响应城区信息
    return jsonify(errno=RET.OK, data=area_dict_list)
