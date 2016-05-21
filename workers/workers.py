# coding: utf-8
"""
    workers.py
    ``````````

    Celery任务队列
"""

from xueer import celery
from xueer import rds
from datetime import timedelta


@celery.task(name='restart_keywords_redis')
def restart_keywords_redis():
    """
    每3天清空一次搜索词纪录
    """
    # 清空搜索词中的所有记录
    rds.flushdb()
    rds.save()


# celery workers
CELERYBEAT_SCHEDULE = {
    'restart_redis_every_259200s': {
        'task': 'restart_keywords_redis',
        'schedule': timedelta(seconds=10)
    },
}
