# coding: utf-8
"""
这段代码确实有点恶心, 需要重构
恶心的地方首先是条件太多, 条件太多没办法, 不得不导致面条式的编程
然后搜索的部分逻辑似乎也添加在了这里, 这个完全可以放到搜索部分完成
现在搜索的逻辑代码就是 models + API, 能不能划分的更细一点?
我先把代码整体读一遍, 然后想想如何划分如何重构!
"""

from flask import jsonify, url_for, request, current_app
from flask_login import current_user
from .authentication import auth
from ..models import Courses, User, Tags, CourseCategories, Search,  Teachers, KeyWords
from . import api
from xueer import db
import json
from sqlalchemy import desc
from flask.ext.paginate import Pagination
"""关于分页, 有没有对资源的装饰器?如果没有如何实现?"""


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
    # 关键字(搜索词): 查询结果或者写入关键字表
    if keywords:
        k = KeyWords.query.filter_by(name=keywords).first()
        if k is None:
            k = KeyWords(name=keywords)
            db.session.add(k)
            db.session.commit()
        k.counts += 1
        """keyword 计数: 其实可以写一个类似构造器的东西(重写__new__),
        这样这部分代码就可以放到models里面"""
        db.session.add(k)
        db.session.commit()
        """利用whooshalchemy搜索关键字
        Search表是一个建立分词和课程关系的m2m表"""
        searches = Search.query.whoosh_search(keywords).all()
        """条件过滤...这一段比较恶心, 但是没什么好的办法"""
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



@api.route('/search/prefetch/', methods=['GET', 'POST'])
def get_search_prefetch():
    """
    获取搜索结果的十条
    """
    courses = []; course1 = []; course2 = [] ;course3 = []
    keywords = request.args.get('keywords')
    if keywords:
        k = KeyWords.query.filter_by(name=keywords).first()
        if k is None:
            k = KeyWords(name=keywords)
            db.session.add(k)
            db.session.commit()
        k.counts += 1
        db.session.add(k)
        db.session.commit()
        searches = Search.query.whoosh_search(keywords).all()
        if request.args.get('sort') == 'view':
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
                    courses = sorted(course0,  key=lambda course : course.count, reverse=True)[:10]
                else:
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
                    courses = sorted(course0,  key=lambda course : course.count, reverse=True)[:10]
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
                courses = sorted(course0,  key=lambda course : course.count, reverse=True)[:10]

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
                    courses = sorted(course0,  key=lambda course : course.likes, reverse=True)[:10]
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
                    courses = sorted(course0,  key=lambda course : course.likes, reverse=True)[:10]
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
                courses = sorted(course0,  key=lambda course : course.likes, reverse=True)[:10]

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
            courses = list(set(course1+course2+course3))[:10]

    return json.dumps(
        [course.to_json2() for course in courses],
        ensure_ascii=False,
        indent=1
        ), 200




@api.route('/search/hot/', methods=['GET'])
def hot_search():
    list = KeyWords.query.all()
    hots = sorted(list, key=lambda item: item.counts, reverse=True)[:10]
    return json.dumps(
        [keyword.to_json() for keyword in hots],
        ensure_ascii=False,
        indent=1
    ), 200

