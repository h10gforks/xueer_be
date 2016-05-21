# coding: utf-8
"""
    search.py
    ~~~~~~~~~

        学而搜索API

现在这段代码问题很多, 3个函数但是有361行代码,
而且代码中的层级太多(条件太多导致面条式编程),
问题解决

    1. 梳理核心逻辑
    2. 条件太多但是如何减少if...else代码
    3. 分页部分如何减少重复

现在条件多是因为分页条件+搜索条件...这是问题所在
"""

from flask import jsonify, url_for, request, current_app
from flask_login import current_user
from .authentication import auth
from ..models import Courses, User, Tags, CourseCategories, Search,  Teachers, KeyWords
from . import api
from xueer import rds, db
import json
from sqlalchemy import desc
from flask.ext.paginate import Pagination
from .keywords import store_rds


@api.route('/search/', methods=['GET'])
def get_search():
    """
    获取搜索结果
    :param keywords:
    :return: search results
    """
    page = request.args.get('page', 1, type=int)
    courses = []; course1 = []; course2 = [] ;course3 = []
    keywords = request.args.get('keywords')
    if keywords:
        store_rds(keywords)
        searches = Search.query.whoosh_search(keywords).all()
        if request.args.get('sort') == 'view':
            if request.args.get('main_cat'):
                if request.args.get('ts_cat'):
                    #对教师进行搜索
                    """根据老师名字搜索课程"""
                    course3 = Courses.query.whoosh_search(keywords).filter_by(
                                type_id=request.args.get('ts_cat'),
                                category_id=request.args.get('main_cat')
                            ).all()
                    # 对标签进行搜索
                    """标签是不需要分词的
                    获取tags对应的课程列表"""
                    tags = Tags.query.whoosh_search(keywords).all()
                    for tag in tags:
                        if tag.courses is not None:
                            course2 = [c.courses for c in tag.courses.all()
                                       if c.courses.category_id=='main_cat' and c.courses.type_id=='ts_cat']
                    #根据课程名搜索
                    for search in searches:
                        if search.courses is not None:
                            course1 += search.courses.filter_by(
                                type_id=request.args.get('ts_cat'),
                                category_id=request.args.get('main_cat')
                            ).all()
                    course0 = list(set(course1 + course2 + course3))
                    courses = sorted(course0,  key=lambda course : course.count, reverse=True)
                else:
                    """这一段完全可以写成函数啊"""
                    #对教师进行搜索
                    course3 = Courses.query.whoosh_search(keywords).filter_by(
                                category_id=request.args.get('main_cat')
                            ).all()
                    #对标签进行搜索
                    tags = Tags.query.whoosh_search(keywords).all()
                    for tag in tags:
                        if tag.courses is not None:
                            for ct in tag.courses.all():
                                course2 = [c.courses for c in tag.courses.all() if c.courses.category_id=='main_cat']
                    #根据课程名搜索
                    for search in searches:
                        if search.courses is not None:
                            course1 += search.courses.filter_by(
                                category_id=request.args.get('main_cat')
                            ).all()
                    course0 = list(set(course1 + course2 + course3))
                    courses = sorted(course0,  key=lambda course : course.count, reverse=True)
                    """"""
            else:
                #对教师进行搜索
                course3 = Courses.query.whoosh_search(keywords).all()
                #对标签进行搜索
                tags = Tags.query.whoosh_search(keywords).all()
                for tag in tags:
                    if tag.courses is not None:
                        course2 = [c.courses for c in tag.courses.all()]
                #根据课程名搜索
                for search in searches:
                    if search.courses is not None:
                        course1 += search.courses.all()
                course0 = list(set(course1 + course2 + course3))
                courses = sorted(course0,  key=lambda course : course.count, reverse=True)

        elif request.args.get('sort') == 'like':
            if request.args.get('main_cat'):
                if request.args.get('ts_cat'):
                    #对教师进行搜索
                    course3 = Courses.query.whoosh_search(keywords).filter_by(
                                type_id=request.args.get('ts_cat'),
                                category_id=request.args.get('main_cat')
                            ).all()
                    #对标签进行搜索
                    tags = Tags.query.whoosh_search(keywords).all()
                    for tag in tags:
                        if tag.courses is not None:
                            course2 = [c.courses for c in tag.courses.all()
                                       if c.courses.category_id=='main_cat' and c.courses.type_id=='ts_cat']
                    #根据课程名搜索
                    for search in searches:
                        if search.courses is not None:
                            course1 += search.courses.filter_by(
                                type_id=request.args.get('ts_cat'),
                                category_id=request.args.get('main_cat')
                            ).all()
                    course0 = list(set(course1 + course2 + course3))
                    courses = sorted(course0,  key=lambda course : course.likes, reverse=True)
                else:
                    #对教师进行搜索
                    course3 = Courses.query.whoosh_search(keywords).filter_by(
                                category_id=request.args.get('main_cat')
                            ).all()
                    #对标签进行搜索
                    tags = Tags.query.whoosh_search(keywords).all()
                    for tag in tags:
                        if tag.courses is not None:
                            course2 = [c.courses for c in tag.courses.all() if c.courses.category_id=='main_cat']
                   #根据课程名搜索
                    for search in searches:
                        if search.courses is not None:
                            course1 += search.courses.filter_by(
                                category_id=request.args.get('main_cat')
                            ).all()
                    course0 = list(set(course1 + course2 + course3))
                    courses = sorted(course0,  key=lambda course : course.likes, reverse=True)
            else:
                #对教师进行搜索
                course3 = Courses.query.whoosh_search(keywords).all()
                #对标签进行搜索
                tags = Tags.query.whoosh_search(keywords).all()
                for tag in tags:
                    if tag.courses is not None:
                        course2 = [c.courses for c in tag.courses.all()]
                #根据课程名搜索
                for search in searches:
                    if search.courses is not None:
                        course1 += search.courses.all()
                course0 = list(set(course1 + course2 + course3))
                courses = sorted(course0,  key=lambda course : course.likes, reverse=True)

        else:
                #对教师进行搜索
            course3 = Courses.query.whoosh_search(keywords).all()
                #对标签进行搜索
            tags = Tags.query.whoosh_search(keywords).all()
            for tag in tags:
                if tag.courses is not None:
                    course2 = [c.courses for c in tag.courses.all()]
                #根据课程名搜索
            for search in searches:
                if search.courses is not None:
                    course1 += search.courses.all()
            courses = list(set(course1+course2+course3))
        pagination = Pagination(
               page=page,
               total=len(courses),
               per_page=current_app.config['XUEER_COURSES_PER_PAGE'],
               error_out=False
        )
        prev = ""
        if pagination.has_prev:
            prev = url_for('api.get_search', page=page-1)
        next = ""
        if pagination.has_next:
            next = url_for('api.get_search', page=page+1)
        courses_count = len(courses)
        if courses_count%current_app.config['XUEER_COURSES_PER_PAGE'] == 0:
            page_count = courses_count//current_app.config['XUEER_COURSES_PER_PAGE']
        else:
            page_count = courses_count//current_app.config['XUEER_COURSES_PER_PAGE']+1
        last = url_for('api.get_search', page=page_count, _external=True)
        courses = courses[(page-1)*20:page*20]
    return json.dumps(
        [course.to_json2() for course in courses],
        ensure_ascii=False,
        indent=1
        ), 200,{'link':'<%s>;rel="next",<%s>;rel="last"' % (next, last)}


@api.route('/search/hot/', methods=['GET'])
def hot_search():
    list = KeyWords.query.all()
    hots = sorted(list, key=lambda item: item.counts, reverse=True)[:10]
    return json.dumps(
        [keyword.to_json() for keyword in hots],
        ensure_ascii=False,
        indent=1
    ), 200
