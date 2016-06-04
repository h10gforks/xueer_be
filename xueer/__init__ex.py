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
from sqlalchemy import create_engine
from xueer_config import config
from celery import Celery


app = Flask(__name__)
app.config.from_object(config['product'])
# app.config.from_object(config['develop'])


db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'
moment = Moment(app)
# initial redis database for keywords store
rds = redis.StrictRedis(host='localhost', port=6380, db=0)
# initial redis database for LRU cache
lru = redis.StrictRedis(host='localhost', port=6385, db=1)


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


from hello import hello
app.register_blueprint(hello)

from auth import auth as auth_blueprint
app.register_blueprint(auth_blueprint, url_prefix='/auth')

from api_1_0 import api as api_1_0_blueprint
app.register_blueprint(api_1_0_blueprint, url_prefix='/api/v1.0')

from admin import admin as admin_blueprint
app.register_blueprint(admin_blueprint, url_prefix='/admin')
