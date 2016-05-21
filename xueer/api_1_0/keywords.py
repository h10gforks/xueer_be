# coding: utf-8
"""
    keywords.py
    ```````````

    学而热搜词统计

    目前的想法是使用redis键值对存储热搜词和计数,
    每三天进行一次重启清空
    将redis任务放到celery队列中进行管理, 方便redis进程的调度
"""

from xueer import rds


def store_rds(keywords):
    """
    将keywords存入redis数据库
    :param keywords: 需存入redis的关键字
    :return None:
    数据存储在硬盘上
    """
    lambda rds: rds.incr(keywords) if rds.get(keywords) else rds.set(keywords, 1)
    rds.save()
