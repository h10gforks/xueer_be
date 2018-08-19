# coding: utf-8
"""
    workers.py
    ``````````

    Celery任务队列
"""

from xueer import make_celery
from xueer import app
from xueer import rds
import os


celery = make_celery(app)


@celery.task(name='restart_keywords_redis')
def restart_keywords_redis():
    """
    每3天清空一次搜索词纪录
    """
    # 搜索词超过100个，就删除100位之后的搜索词
    count = rds.zcard("sortedSet")
    if count > 100:
        rds.zremrangebyrank("sortedSet", 0, count-100)


@celery.task(name='dump_progres_db')
def dump_progresql_db():
    """
    每天12点定时备份学而数据库
    ~~~> pg_dump
    """
    # 转交给 postgres 用户的 crontab 处理
