# coding: utf-8
"""
    courses.py
    ``````````

    : 课程API

    : GET /api/v1.0/courses/: 获取全部课程信息
    : GET /api/v1.0/courses/id/: 获取特定id课程信息
    : POST(admin) /api/v1.0/courses/: 创建一个新的课程 admin
    : PUT(admin) /api/v1.0/courses/id/: 更新特定id课程的信息
    : DELETE(admin) /api/v1.0/courses/id/: 删除特定id课程
    : GET /api/v1.0/tags/id/courses/: 获取特定id tag的所有课程
    .........................................................

"""

from flask import jsonify, url_for, request, current_app
from ..models import Courses, Tags
from . import api
from xueer import db, lru
import json
from xueer.decorators import admin_required


def pagination(lit, page, perpage):
    """

    :param lit:分页对象列表
    :param page: 当前页
    :param perpage: 每页的数量
    :return: 返回当前分页的列表对象,
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


def get_cat_courses(gg_cat=0, ts_cat=0, zy_cat=0, sz_cat=0, sub_cat=0):
    """
    根据特定类别id获取特定类别课程集
    """
    courses = []

    if gg_cat:
        gg_courses = Courses.query.filter_by(category_id=1).all()
        courses.extend(gg_courses)
    if ts_cat:
        if sub_cat:
            ts_courses = Courses.query.filter_by(subcategory_id=sub_cat).all()
        else:
            ts_courses = Courses.query.filter_by(category_id=2).all()
        courses.extend(ts_courses)
    if zy_cat:
        zy_courses = Courses.query.filter_by(category_id=3).all()
        courses.extend(zy_courses)
    if sz_cat:
        sz_courses = Courses.query.filter_by(category_id=4).all()
        courses.extend(sz_courses)

    if not (gg_cat+ts_cat+zy_cat+sz_cat):
        all_courses = Courses.query.all()
        courses.extend(all_courses)
    return courses


@api.route('/courses/', methods=["GET"])
def get_courses():
    global paginate
    gg_cat = request.args.get('gg_cat') or '0'
    ts_cat = request.args.get('ts_cat') or '0'
    zy_cat = request.args.get('zy_cat') or '0'
    sz_cat = request.args.get('sz_cat') or '0'
    sub_cat = request.args.get('sub_cat') or '0'
    page = request.args.get('page', 1, type=int) or '1'
    per_page = request.args.get('per_page', type=int) or '20'
    sort = request.args.get('sort') or 'view'
    current_app.config['XUEER_COURSES_PER_PAGE'] = int(per_page)
    courses = get_cat_courses(int(gg_cat), int(ts_cat), int(zy_cat), int(sz_cat), int(sub_cat))

    if sort == 'view':
        courses = sorted(courses, key=lambda c: c.count, reverse=True)
    elif sort == 'like':
        courses = sorted(courses, key=lambda c: c.likes, reverse=True)
    elif sort == 'score':
        courses = sorted(courses, key=lambda c: c.score, reverse=True)

    pagination_lit = pagination(courses, int(page), int(per_page))
    current = pagination_lit[0]
    next_page = pagination_lit[1][0]
    last_page = pagination_lit[1][1]
    return json.dumps(
        [course.to_json2() for course in current],
        ensure_ascii=False,
        indent=1
    ), \
        200, {'link': '<%s>; rel="next", <%s>; rel="last"'
     % (next_page, last_page)}


@api.route('/courses/<int:id>/', methods=["GET"])
def get_course_id(id):
    course = Courses.query.get_or_404(id)
    return jsonify(course.to_json())


@api.route('/courses/', methods=["GET", "POST"])
@admin_required
def new_course():
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
    course = Courses.query.get_or_404(id)
    if request.method == "PUT":
        # eval is evil:( but
        #warning: do not use eval,use `json.loads()` instead!!!
        # data_dict = eval(request.data)
        data_dict=json.loads(request.date)
        course.name = data_dict.get('name', course.name)
        course.teacher = data_dict.get('teacher', course.teacher)
        course.category_id = data_dict.get('category_id', course.category_id)
        course.subcategory_id = data_dict.get('sub_category_id',
            course.subcategory_id)
        course.type_id = data_dict.get('type_id', course.type_id)
        course.available=data_dict.get('available',course.available)
        db.session.add(course)
        db.session.commit()
    return jsonify({'update': id}), 200


@api.route('/courses/<int:id>/', methods=['GET', 'DELETE'])
@admin_required
def delete_course(id):
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
    tag = Tags.query.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    paginate = tag.courses.paginate(
        page, error_out=False,
        per_page=current_app.config["XUEER_COURSES_PER_PAGE"]
    )
    course_tags = paginate.items  # 获取分页的courses对象
    courses = []
    prev = ""
    next = ""
    if paginate.has_prev:
        prev = url_for('api.get_tags_id_courses', id=id, page=page-1)
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


