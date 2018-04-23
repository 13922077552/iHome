# -*- coding:utf-8 -*-
import redis
import logging

class Config(object):
    DEBUG = True
    # 设置连接数据库的URL
    SQLALCHEMY_DATABASE_URI = "mysql://root:mysql@127.0.0.1:3306/iHome_GZ01"
    # 设置每次请求结束后会自动提交数据库中的改动
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # redis数据库配置
    REDIS_HOST = '127.0.0.1'
    REDIS_PORT = 6379

    # 配置session参数
    # 指定sesion存储到redis
    SESSION_TYPE = 'redis'
    # 指定要使用的redis位置
    SESSION_REDIS = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT)
    # 开启session数据的签名。混淆
    SESSION_USE_SIGNER = True
    # 设置session有效期：这里指的是session的扩展操作session时设置的有效期限
    PERMANENT_SESSION_LIFETIME = 3600 * 24   # 一天

    # 秘钥
    SECRET_KEY = 'q7pBNcWPgmF6BqB6b5VICF7z7pI+90o0O4CaJsFGjzRsYiya9SEgUDytXvzFsIaR'


class Development(Config):
    """开发模式下的配置"""

    # 日志调试等级
    LOGGING_LEVEL = logging.DEBUG


class Production(Config):
    """生产环境。线上。部署之后"""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = "mysql://root:mysql@127.0.0.1:3306/ihome01"
    PERMANENT_SESSION_LIFETIME = 3600 * 24 * 2   # 2天

    # 日志调试等级
    LOGGING_LEVEL = logging.WARN

class UnitTest(Config):
    """测试环境"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "mysql://root:mysql@127.0.0.1:3306/ihome_unittest"


# 准备工厂要使用的原材料
config = {
    'dev': Development,
    'test': UnitTest,
    'pro': Production
}