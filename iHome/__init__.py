# -*- coding:utf-8 -*-
# 创建应用实例
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import redis
from flask_session import Session
from config import config
from flask_wtf.csrf import CSRFProtect
from iHome.utils.common import RegexConverter
import logging
from logging.handlers import RotatingFileHandler

# 创建链接mysql数据库的对象
db = SQLAlchemy()
# 定义一个全局的redis_store
redis_store = None


def setUpLogging(leverl):
    """根据开发环境设置入职等级"""

    # 设置日志的记录等级
    logging.basicConfig(level=leverl)  # 调试debug级
    # 创建⽇志记录器，指明⽇志保存的路径、每个⽇志⽂件的最⼤⼤⼩、保存的⽇志⽂件个数上限
    file_log_handler = RotatingFileHandler("logs/log", maxBytes=1024 * 1024 * 100, backupCount=10)
    # 创建⽇志记录的格式 ⽇志等级 输⼊⽇志信息的⽂件名 ⾏数 ⽇志信息
    formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
    # 为刚创建的⽇志记录器设置⽇志记录格式
    file_log_handler.setFormatter(formatter)
    # 为全局的⽇志⼯具对象（flask app使⽤的）添加⽇志记录器
    logging.getLogger().addHandler(file_log_handler)


def get_app(config_name):
    """使用工厂设置模式，传入不同的config_name，找到模式的配置"""
    # 根据开发环境设置日志等级
    setUpLogging(config[config_name].LOGGING_LEVEL)

    app = Flask(__name__)

    # 加载配置参数
    app.config.from_object(config[config_name])

    # 创建连接mysql数据库的对象
    db.init_app(app)

    # 创建连接到redis数据库的对象
    global redis_store
    redis_store = redis.StrictRedis(host=config[config_name].REDIS_HOST, port=config[config_name].REDIS_PORT)

    # 开启CSRF保护：flask需要自己将csrf_token写入游览器的cookie
    CSRFProtect(app)

    # 使用flask_session将session数据写入到redis数据库
    Session(app)

    # 将自定义的路由转换器添加转换器列表
    # 要将注册放在注册蓝图之前，不然蓝图注册蓝图之后，蓝图路由调用不了自定义转换器
    app.url_map.converters['re'] = RegexConverter

    from iHome.web_html import html_blue
    from iHome.api_1_0 import api
    # 创建蓝图
    app.register_blueprint(api)
    app.register_blueprint(html_blue)

    return app
