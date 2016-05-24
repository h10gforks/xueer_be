# coding: utf-8
"""
    workers.py
    ``````````

    Celery任务队列
"""

from xueer import make_celery
from xueer import app
from xueer import rds


celery = make_celery(app)


@celery.task(name='restart_keywords_redis')
def restart_keywords_redis():
    """
    每3天清空一次搜索词纪录
    """
    # 清空搜索词中的所有记录
    rds.flushdb()
    rds.save()
