# coding: utf-8

"""
    config.py
    ~~~~~~~~~

        配置文件
        返回一个配置字典
"""

# the root url of this flask application
import os
# from workers.workers import restart_keywords_redis
from datetime import timedelta
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    """
    配置基类
        密钥配置、数据库配置、管理员配置、参数配置
    """
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'I hate flask hahahaha'
    # app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'xueer_test.sqlite')
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    XUEER_COMMENTS_PER_PAGE = 10
    XUEER_COURSES_PER_PAGE = 20
    XUEER_USERS_PER_PAGE = 20
    XUEER_TAGS_PER_PAGE = 20
    XUEER_TIPS_PER_PAGE = 5
    CELERYBEAT_SCHEDULE = {}

    @staticmethod
    def init_app(app):
        pass


class DevConfig(Config):
    """
    开发环境下配置
        开启调试器
        数据库采用sqlite数据库
        测试管理员账号
    """
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('XUEER_POSTGRES_URI') or 'sqlite:///' + os.path.join(basedir, 'xueer_dev.sqlite')
    CELERY_BROKER_URL = 'redis://localhost:6382/0'
    CELERY_RESULT_BACKEND = 'redis://localhost:6382/0'
    CELERYBEAT_SCHEDULE = {
        'restart_redis_every_259200s': {
            'task': 'restart_keywords_redis',
            'schedule': timedelta(seconds=259200)
        },
    }


class ProConfig(Config):
    """
    生产环境下配置
    """
    SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI")
    CELERY_BROKER_URL = 'redis://localhost:6382/0'
    CELERY_RESULT_BACKEND = 'redis://localhost:6382/0'
    CELERYBEAT_SCHEDULE = {
        'restart_redis_every_259200s': {
            'task': 'restart_keywords_redis',
            'schedule': timedelta(seconds=259200)
        },
    }


class TestConfig(Config):
    """
    测试环境下配置
    """
    DEBUG = True


config = {
    'develop': DevConfig,
    'product': ProConfig,
    'testing': TestConfig,
    'default': DevConfig
}
