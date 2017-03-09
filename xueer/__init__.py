# coding: utf-8
"""
    __init__.py
    ```````````

    : Flask app创建
    : Flask 扩展初始化
    : Flask 蓝图注册
    .................

    : copyright: (c) 2016 by MuxiStudio
    : license: MIT

"""
import os

import redis
from flask import Flask
from flask_moment import Moment
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from celery import Celery

from xueer_config import config


# Flask extensions
db = SQLAlchemy()
login_manager = LoginManager()
moment = Moment()

# Initial redis for keywords store
rds = redis.StrictRedis(host='localhost', port=6380, db=0, password="foobared6380")
# Initial redis for LRU/memory cache
lru = redis.StrictRedis(host='localhost', port=6385, db=1, password="foobared6385")

from . import models


def create_app(config_name=None, main=True):
    """
    学而app工厂函数

    :param config_name: 当前配置环境
    :param main: 主进程模块名称
    """
    if config_name is None:
        config_name = os.environ.get('XUEER_CONFIG', 'default')
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Initial flask extensions
    db.init_app(app)
    login_manager.init_app(app)
    moment.init_app(app)

    # blueprints
    from hello import hello
    app.register_blueprint(hello)

    from auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    from api_1_0 import api as api_1_0_blueprint
    app.register_blueprint(api_1_0_blueprint, url_prefix='/api/v1.0')

    from admin import admin as admin_blueprint
    app.register_blueprint(admin_blueprint, url_prefix='/admin')

    return app


# xueer app
app = create_app(config_name = os.getenv('XUEER_CONFIG') or 'default')


# setting up celery
def make_celery(app):
    celery = Celery(app.import_name, broker=app.config['CELERY_BROKER_URL'])
    celery.conf.update(app.config)
    TaskBase = celery.Task
    class ContextTask(TaskBase):
        abstract = True
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    celery.Task = ContextTask
    return celery
