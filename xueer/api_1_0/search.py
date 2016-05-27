# coding: utf-8
"""
    search.py
    `````````

    xueer search api
"""

from . import api
from flask import request
from xueer import rds, lru
import json


@api.route('/search/', methods=['GET'])
def search():
    """
    搜索API
    """
    keywords = request.args.get('keywords')         # 搜索词(存入redis)
    page = int(request.args.get('page')) or 1       # 分页页数
    sort = request.args.get('sort')                 # 返回数据排序('views', 'likes')
    main_cat = request.args.get('main_cat')         # 主分类
    ts_cat = request.args.get('ts_cat')             # 二级分类(仅限通识课)
    # 搜索匹配
    results = []
    courses = lru.keys()
    for course in courses:
        searchs = lru.get(course)
        for search in searchs:
            if keywords in search:
                result.append(course)
    # 热搜词存储
    rds.set(keywords, 1) \
        if rds.get(keywords) is None \
        else rds.incr(keywords)
    # 结果集返回
    return json.dumps(
        [course.to_json() for course in results],
        ensure_ascii=False,
        indent=1
    ), 200
