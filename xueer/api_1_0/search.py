# coding: utf-8
"""
    search.py
    `````````

    xueer search api
"""

from . import api
from flask import request, url_for
from xueer import rds, lru
from xueer.models import Tags, Courses
from .paginate import pagination
from .kmp import kmp
import json


def category_catch(keywords, main_cat_id=0, ts_cat_id=0):
    """
    类别筛选
    """
    category = {
        1: '公共课', 2:'通识课',
        3: '专业课', 4:'素质课'
    }.get(main_cat_id)
    subcategory = {
        1: '通识核心课',
        2: '通识选修课'
    }.get(ts_cat_id)
    if category and not subcategory:
        gen = (course_json for course_json in lru.keys() \
                if eval(course_json).get('main_category') == category)
    elif subcategory:
        gen = (course_json for course_json in lru.keys() \
                if eval(course_json).get('sub_category') == subcategory)
    else:
        gen = lru.keys()
    results = []; courses = []; sort = {};
    for course_json in gen:
        searchs = lru.get(course_json)
        if keywords in eval(searchs)[0]:
            sort[course_json] = kmp(eval(searchs)[0], keywords)
            sorted_list = sorted(sort.iteritems(), key=lambda d: d[1])
            results = [eval(c_json[0]) for c_json in sorted_list]
        elif keywords in eval(searchs)[1]:
            results.append(eval(course_json))
        elif len(eval(searchs)) == 3 and \
            keywords == eval(searchs)[2]:
            results.append(eval(course_json))
    if len(results) == 0:
        tag = Tags.query.filter_by(name=keywords).first()
        if tag:
            course_tags = tag.courses.all()
            for course_tag in course_tags:
                courses.append(Courses.query.get_or_404(course_tag.course_id))
                for course in courses:
                    # here I set memcache
                    lru.set(course.to_json(), [course.name, course.teacher, keywords])
                    results.append(course.to_json())
    return results


@api.route('/search/', methods=['GET'])
def search():
    """
    搜索API
    """
    keywords = request.args.get('keywords')
    page = request.args.get('page') or '1'
    per_page = request.args.get('per_page') or '20'
    sort = request.args.get('sort') or 'view'
    main_cat = request.args.get('main_cat') or '0'
    ts_cat = request.args.get('ts_cat') or '0'
    # 搜索条件匹配
    results = category_catch(keywords, int(main_cat), int(ts_cat))
    # 热搜词存储
    rds.set(keywords, 1) \
        if rds.get(keywords) is None \
        else rds.incr(keywords)
    # 排序规则
    if sort == 'view':
        results = sorted(results, key = lambda json: json.get('views'), reverse=True)
    elif sort == 'like':
        results = sorted(results, key = lambda json: json.get('likes'), reverse=True)
    # 对结果集分页返回返回
    pagination_lit = pagination(results, int(page), int(per_page))
    current = pagination_lit[0]
    next_page = pagination_lit[1][0]
    last_page = pagination_lit[1][1]
    return json.dumps(
        current,
        ensure_ascii=False,
        indent=1
    ), 200, {
        'link': '<%s>; rel="next", <%s>; rel="last"' % (next_page, last_page)}


@api.route('/search/hot/', methods=['GET'])
def hot():
    """
    返回最热的10个搜索词
    """
    words = rds.keys()
    hot_words = sorted(words, key=lambda w: int(rds.get(w)), reverse=True)[:10]
    return json.dumps(hot_words), 200
