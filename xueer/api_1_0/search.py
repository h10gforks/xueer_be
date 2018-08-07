# coding: utf-8
"""
    search.py
    `````````

    : xueer search api

    : GET /api/v1.0/search/: 返回搜索结果集
    : GET /api/v1.0/search/hot/: 返回全站热搜词
    ............................................

""" 
from . import api
from flask import request, url_for, jsonify
from xueer import rds, lru
from xueer.models import Tags, Courses
from xueer.decorators import admin_required,moderator_required
from .paginate import pagination
from .kmp import kmp
import json

lrukeys = lru.keys()

@api.route("/refresh_memcache/", methods = ["GET"])
@moderator_required
def refresh_keys():
    global lrukeys
    lrukeys=lru.keys()
    return jsonify({
            "msg":"ok"
        }), 200

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
        gen = (course_json for course_json in lrukeys \
                if eval(course_json).get('main_category') == category)
    elif subcategory:
        gen = (course_json for course_json in lrukeys \
                if eval(course_json).get('sub_category') == subcategory)
    else:
        gen = lrukeys
    results = []; courses = []; sort = {};
    for course_json in gen:
        #searchs = lru.get(course_json)
        #不再从lru中拿，而是直接从course_json中获取
        #因为从redis中获取时间太长(每个0.04s, 100个课4秒)
        searchs = []
        course_json = eval(course_json)
        searchs.append(course_json['title'])
        searchs.append(course_json['teacher'])
        searchs.append(course_json['hot_tags'])
        searchs = str(searchs)
        course_json = str(course_json)

        if keywords in eval(searchs)[0]:
            sort[course_json] = kmp(eval(searchs)[0], keywords)
            sorted_list = sorted(sort.iteritems(), key=lambda d: d[1])
            results = [eval(c_json[0]) for c_json in sorted_list]
        elif keywords in eval(searchs)[1]:
            results.append(eval(course_json))
        elif len(eval(searchs)) == 3 and
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


def new_category_catch(keywords, main_cat_id=0, ts_cat_id=0):
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

    lrukeys = lru.keys()

    if category and not subcategory:
        gen = (course_json for course_json in lrukeys \
                if eval(course_json).get('main_category') == category)
    elif subcategory:
        gen = (course_json for course_json in lrukeys \
                if eval(course_json).get('sub_category') == subcategory)
    else:
        gen = lrukeys

    primary_result = []; secondary_result = []; third_result = []; sorts = {};
    for course_json in  gen:
        course_json = eval(course_json)
        title = course_json['title']
        teacher = course_json['teacher']
        hot_tags = course_json['hot_tags']
        course_json = str(course_json)

        if keywords in title:
            sorts[course_json] = kmp(eval(title, keywords))
        elif keywords in teacher:
            secondary_result.append(course_json)
        elif keywords in hot_tags:
            secondary_result.append(course_json)

    if len(sorts) != 0:
        sorted_list = sorted(sorts.iteritems(), key=lambda d: d[1])
        primary_result = [eval(course_json) for course_json in sorted_list ]

    if len(primary_result) == 0 and len(secondary_result) == 0:
        tag = Tags.query.filter_by(name=keywords).first()
        if tag:
            course_tags = tag.courses.all()
            for course_tag in course_tags:
                course_ = Courses.query.get_or_404(course_tag.course_id)
                third_result.append(course_.to_json())

        course = Courses.query.filter_by(name=keywords).first()
        if course:
            third_result.append(course.to_json())

        for course_json in third_result:
            lru.lpush("lruList",course_json)

    elif len(primary_result) != 0:
        for course_json in primary_result:
            lru.lrem("lruList",course_json,1)
        for course_json in primary_result:
            lru.lpush("lruList",course_json)

    elif len(secondary_result) != 0:
        for course_json in secondary_result:
            lru.lrem("lruList",course_json,1)
        for course_json in secondary_result:
            lru.lpush("lruList",course_json)

    lru_len = lru.llen("lruList")
    while lru_len > 50:
        lru.rpop("lruList")
        lru_len = lru_len - 1

    if len(primary_result) != 0:
        return primary_result
    elif len(secondary_result) != 0:
        return secondary_result
    else:
        return third_result


@api.route('/search/', methods=['GET'])
def search():
    """
    搜索API
    """
    keywords = request.args.get('keywords')
    page = request.args.get('page') or '1'
    per_page = request.args.get('per_page') or '20'
    main_cat = request.args.get('main_cat') or '0'
    ts_cat = request.args.get('ts_cat') or '0'
    # 搜索条件匹配
    #results = category_catch(keywords, int(main_cat), int(ts_cat))
    results = new_category_catch(keywords, int(main_cat), int(ts_cat))
    # 热搜词存储
    #rds.set(keywords, 1) \
    #    if rds.get(keywords) is None \
    #    else rds.incr(keywords)
    exist = rds.zscore("sortedSet",keywords)
    if exist == None:
        rds.zadd("sortedSet",keywords,1)
    else:
        rds.incrby("sortedSet",keywords,1)
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
    #words = rds.keys()
    hot_words = rds.zrange("sortedSet",0,9,desc=True)
    #hot_words = sorted(words, key=lambda w: int(rds.get(w)), reverse=True)[:10]
    return json.dumps(hot_words), 200
