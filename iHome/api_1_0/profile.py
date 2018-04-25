# -*- coding: utf-8 -*-

from flask import session, jsonify, current_app, request, g
from iHome.models import User, House
from iHome.utils.response_code import RET
from . import api
from iHome.utils.image_storage import upload_image
from iHome import constants, db
from iHome.utils.common import login_required


@api.route('/users/houses', methods=['GET'])
@login_required
def get_user_house():
    """我的房源
    0.判断是否登录
    1.获取当前用户的id
    2.查询该用户的所有房屋
    3.构造响应数据
    4.返回数据
    """
    # 1.获取当前用户的id
    user_id = g.user_id

    # 2.查询该用户的所有房屋
    try:
        houses = House.query.filter(House.user_id == user_id).all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查询房屋数据失败")

    # 3.构造响应数据
    heuse_dict_list = []
    for house in houses:
        heuse_dict_list.append(house.to_basic_dict())

    # 4.返回数据
    return jsonify(errno=RET.OK, errmsg="OK", data=heuse_dict_list)




@api.route('/users/auth', methods=['GET'])
@login_required
def get_user_auth():
    """提供实名认证数据
    0.判断用户是否登录
    1.查询当前登录用户user信息
    2.构造响应的实名认证的数据
    3.响应实名认证的数据
    """
    # 1.查询当前登录用户user信息
    user_id = g.user_id
    try:
        user = User.query.get(user_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查询用户数据失败")
    if not user:
        return jsonify(errno=RET.NODATA, errmsg="用户不存在")

    # 2.构造响应的实名认证的数据
    response_auth_dict = user.auth_to_dict()

    # 3.响应实名认证的数据
    return jsonify(errno=RET.OK, errmsg='OK', data=response_auth_dict)


@api.route('/users/auth', methods=['POST'])
@login_required
def set_user_auth():
    """实名认证
    0.判断是否登录
    1.获取实名认证参数，real_name,id_card，并判断是否为空
    2.查询当前的登录用户user模型
    3.将real_name,id_card赋值给user模型
    4.保存到数据库
    5.响应实名认证结束
    """

    # 1.获取实名认证参数，real_name, id_card，并判断是否为空
    json_dict = request.json
    real_name = json_dict.get('real_name')
    id_card = json_dict.get('id_card')

    if not all([real_name, id_card]):
        return jsonify(errno=RET.PARAMERR, errmsg="缺少参数")

    # 2.查询当前的登录用户user模型
    user_id = g.user_id
    try:
        user = User.query.get(user_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查询用户失败")
    if not user:
        return jsonify(errno=RET.NODATA, errmsg="用户不存在")

    # 3.将real_name,id_card赋值给user模型
    user.real_name = real_name
    user.id_card = id_card

    # 4.保存到数据库
    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="保存数据失败")

    # 5.响应认证结果
    return jsonify(errno=RET.OK, errmsg="认证成功")


@api.route('/users/name', methods=['PUT'])
@login_required
def set_user_name():
    """修改用户名
    0.TODO 判断用户是否登录
    1.获取新的用户名，并判断是否为空
    2.查询当前的登录用户
    3.将新的用户名赋值给当前登录用户的user模型
    4.将数据保存到数据库
    5.响应修改用户的结果
    """
    # 1.获取新的用户名，并判断是否为空
    json_dict = request.json
    new_name = json_dict.get('name')
    if not new_name:
        return jsonify(errno=RET.PARAMERR, errmsg="缺少参数")

    # 2.查询当前登录的⽤户
    user_id = session.get('user_id')
    try:
        user = User.query.get(user_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查询数据库失败")
    if not user:
        return jsonify(errno=RET.NODATA, errmsg="用户不存在")

    # 3.将新的用户名赋值给当前登录用户的user模型
    user.name = new_name
    # 4.将数据保存到数据库
    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="保存数据失败")
    session['name']=new_name

    # 5.响应修改用户的结果
    return jsonify(errno=RET.OK, errmsg="修改用户名成功")


@api.route('/users/avatar', methods=['POST'])
@login_required
def upload_avatar():
    """上传用户头像
    0.TODO 判断用户是否登录
    1.获取用户上传的头像数据
    2.调用上传图片的方法，上传头像到七牛云
    3.上传如果成功，储存图片唯一标识到数据库
    4.如果上传成功响应结果
    """

    # 1.获取用户上传的头像数据
    try:
        # 用files取文件的内容取不到会报错，
        image_data = request.files.get('avatar')
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DATAERR, errmsg="图像获取失败")

    # 2.调用上传图片的方法，上传头像到七牛云
    try:
        key = upload_image(image_data)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR, errmsg="上传图像失败")

    # 3.上传如果成功，储存图片唯一标识到数据库
    # 用户头像要和用户绑定，所有要查出是谁在上传头像
    user_id = session.get('user_id')
    try:
        user = User.query.get(user_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查询用户失败")
    # 储存key到avatar_url
    user.avatar_url = key
    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="存储⽤户头像失败")

    # 4.如果上传成功响应结果
    avatar_url = constants.QINIU_DOMIN_PREFIX + key
    return jsonify(errno=RET.OK, errmsg="上传头像成功", data=avatar_url)


@api.route('/users', methods=['GET'])
@login_required
def get_user_info():
    """ 提供个人信息
        0.TODO:判断当前用户是否登录
        1.获取当前登录用户的user_id
        2.查询出当前登录用户的信息
        3.构造响应数据
        4.响应该登录用户的信息
    """
    # 1.获取当前登录用户的user_id
    user_id = g.user_id

    # 2.查询出当前登录用户的信息2.查询出当前登录用户的信息
    try:
        user = User.query.get(user_id)

    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查询数据失败")
    if not user:
        return jsonify(errno=RET.NODATA, errmsg="用户数据为空")

    # 3.构造响应数据
    # 界面需要说明数据就响应说明数据，或者响应用户所有的信息
    response_info_dict = user.to_dict()

    # 4.响应该登录用户的信息
    return jsonify(errno=RET.OK, errmsg="OK", data=response_info_dict)
