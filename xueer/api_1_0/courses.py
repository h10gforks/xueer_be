# coding: utf-8
"""
    api~courses
    ```````````

    课程API
"""

from flask import jsonify, url_for, request, current_app
from .authentication import auth
from sqlalchemy import desc
from ..models import Courses, User, Tags, CourseCategories, CourseTypes, Permission
from . import api
from xueer import db, lru
import json
from xueer.decorators import admin_required


def pagination(lit, page, perpage):
    """
    返回当前分页的列表对象,
    next、last链接
    {current: next_lit}
    """
    _yu = len(lit) % perpage
    _chu = len(lit) // perpage
    if _yu == 0:
        last = _chu
    else:
        last = _chu + 1
    current = lit[perpage*(page-1): perpage*page]
    next_page = ""
    if page < last:
        next_page = url_for('api.get_courses', page=page+1)
    elif page == last:
        next_page = ""
    last_page = url_for('api.get_courses', page=last)
    return [current, (next_page, last_page)]


def get_cat_courses(main_cat=0, ts_cat=0):
    """
    根据特定类别id获取特定类别课程集
    """
    if main_cat and not ts_cat:
        courses = Courses.query.filter_by(category_id=main_cat)
    elif main_cat and ts_cat:
        courses = Courses.query.filter_by(subcategory_id=ts_cat)
    else:
        courses = Courses.query.all()
    return courses


@api.route('/courses/', methods=["GET"])
def get_courses():
    """
    获取全部课程
    """
    global paginate
    main_cat = request.args.get('main_cat') or '0'
    ts_cat = request.args.get('ts_cat') or '0'
    page = request.args.get('page', 1, type=int) or '1'
    per_page = request.args.get('per_page', type=int) or '20'
    sort = request.args.get('sort') or 'view'
    current_app.config['XUEER_COURSES_PER_PAGE'] = int(per_page)
    courses = get_cat_courses(int(main_cat), int(ts_cat))
    if sort == 'view':
        courses = sorted(courses, key=lambda c: c.count, reverse=True)
    elif sort == 'like':
        courses = sorted(courses, key=lambda c: c.likes, reverse=True)
    pagination_lit = pagination(courses, int(page), int(per_page))
    current = pagination_lit[0]
    next_page = pagination_lit[1][0]
    last_page = pagination_lit[1][1]
    return json.dumps(
        [course.to_json2() for course in current],
        ensure_ascii=False,
        indent=1
    ), 200, {'link': '<%s>; rel="next", <%s>; rel="last"' % (next_page, last_page)}


@api.route('/courses/<int:id>/', methods=["GET"])
def get_course_id(id):
    """
    获取特定id课程的信息
    :param id:
    :return:
    """
    course = Courses.query.get_or_404(id)
    return jsonify(course.to_json())


@api.route('/courses/', methods=["GET", "POST"])
@admin_required
def new_course():
    """
    创建一个新的课程
    :return:
    """
    # request.get_json.get('item', 'default')
    if request.method == "POST":
        course = Courses.from_json(request.get_json())
        db.session.add(course)
        db.session.commit()
        return jsonify({
            'id': course.id
        }), 201


@api.route('/courses/<int:id>/', methods=["GET", "PUT"])
@admin_required
def put_course(id):
    """
    更新一门课
    """
    course = Courses.query.get_or_404(id)
    if request.method == "PUT":
        data_dict = eval(request.data)
        course.name = data_dict.get('name', course.name)
        course.teacher = data_dict.get('teacher', course.teacher)
        course.category_id = data_dict.get('category_id', course.category_id)
        course.subcategory_id = data_dict.get('sub_category_id', course.subcategory_id)
        course.type_id = data_dict.get('type_id', course.type_id)
        db.session.add(course)
        db.session.commit()
    return jsonify({'update': id}), 200


@api.route('/courses/<int:id>/', methods=['GET', 'DELETE'])
@admin_required
def delete_course(id):
    """
    删除一个课程
    :param id:
    :return:
    """
    course = Courses.query.get_or_404(id)
    if request.method == "DELETE":
        db.session.delete(course)
        db.session.commit()
        # 自动清除缓存
        lru.delete(course)
        lru.save()
        return jsonify({
            'message': '该课程已被删除'
        })


@api.route('/tags/<int:id>/courses/')
def get_tags_id_courses(id):
    """
    获取特定id的tag对应的所有课程
    :param id: tag的id
    :return: 该id tag对应的所有课程
    """
    # 根据id获取tag
    tag = Tags.query.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    paginate = tag.courses.paginate(
        page,
        per_page=current_app.config["XUEER_COURSES_PER_PAGE"],
        error_out=False
    )
    course_tags = paginate.items  # 获取分页的courses对象
    courses = []
    prev = ""
    if paginate.has_prev:
        prev = url_for('api.get_tags_id_courses', id=id, page=page-1)
    next = ""
    if paginate.has_next:
        next = url_for('api.get_tags_id_courses', id=id, page=page+1)
    courses_count = tag.courses.count()
    if courses_count % current_app.config['XUEER_TAGS_PER_PAGE'] == 0:
        page_count = courses_count//current_app.config['XUEER_TAGS_PER_PAGE']
    else:
        page_count = courses_count//current_app.config['XUEER_TAGS_PER_PAGE']+1
    last = url_for('api.get_tags_id_courses', id=id, page=page_count)
    for course_tag in course_tags:
        courses.append(Courses.query.get_or_404(course_tag.course_id))
    return json.dumps(
        [course.to_json2() for course in courses],
        ensure_ascii=False,
        indent=1
    ), 200, {'link': '<%s>; rel="next", <%s>; rel="last"' % (next, last)}
