# coding: utf-8
"""
    comments.py
    ```````````

    : 评论API模块
    : -- GET(admin) /api/v1.0/comments/: 获取所有评论
    : -- GET(login) /api/v1.0/comments/id/: 获取特定id的评论, 需登录
    : -- GET /api/v1.0/courses/id/comments/: 获取特定id的课程对应评论
    : -- GET /api/v1.0/courses/id/comments/hot/: 获取特定id课程的热门评论
    : -- POST(login) /api/v1.0/courses/id/comments/: 向特定id课程发表评论
    : -- DELETE(admin) /api/v1.0/comments/id/: 删除特定id的评论
    : -- GET /api/v1.0/tip/id/comments/: 获取特定id的tip所有评论
    : -- POST(login) /api/v1.0/tip/id/comments/: 向特定的tip发表评论
    : -- DELETE(admin) /api/v1.0/tip/tid/comments/id/: 删除特定id tip的特定评论
    ....................................................................

"""
from flask import request, jsonify, url_for, current_app, g
from .. import db
from sqlalchemy import desc
from ..models import Comments, Courses, Tips
from xueer.models import Tags, CourseTag
from . import api
import json
from xueer.api_1_0.authentication import auth
from xueer.decorators import admin_required


comments_per_page = 10


@api.route('/for_app_ctx/')
def for_app_ctx():
    global comments_per_page
    comments_per_page = current_app.config['XUEER_COMMENTS_PER_PAGE']


def add_tags(course):
    """
    判断
        向数据库中添加tag实例
        向数据库中添加tag和course关系
    """
    tags = request.json.get("tags").split()
    # add tag
    for tag in tags:
        tag_in_db = Tags.query.filter_by(name=tag).first()
        if tag_in_db:
            tag_in_db.count += 1
        else:
            add_tag = Tags(name=tag, count=1)
        db.session.add(add_tag)
        db.session.commit()

    # add course & tag
    for tag in tags:
        get_tag = Tags.query.filter_by(name=tag).first()
        course_tags = [tag.tags for tag in course.tags.all()]
        if get_tag in course_tags:
            course_tag = CourseTag.query.filter_by(
                tag_id=get_tag.id, course_id=id,
            ).first()
            course_tag.count += 1
        else:
            course_tag = CourseTag(
                tag_id=get_tag.id, course_id=id, count=1
            )
        db.session.add(course_tag)
        db.session.commit()


@api.route('/comments/', methods=["GET"])
@admin_required
def get_comments():
    page = request.args.get('page', 1, type=int)
    pagination = Comments.query.order_by(desc(Comments.timestamp)).paginate(
        page, per_page=comments_per_page, error_out=False
    )
    comments = pagination.items
    prev = ""
    next = ""
    if pagination.has_prev:
        prev = url_for('api.get_comments', page=page - 1)
    if pagination.has_next:
        next = url_for('api.get_comments', page=page + 1)
    comments_count = len(Comments.query.all())
    if comments_count % comments_per_page == 0:
        page_count = comments_count//comments_per_page
    else:
        page_count = comments_count//comments_per_page
    last = url_for('api.get_comments', page=page_count)
    return json.dumps(
        [comment.to_json() for comment in comments],
        ensure_ascii=False,
        indent=1
    ), 200, {'link': '<%s>; rel="next", <%s>; rel="last"' % (next, last)}


@api.route('/comments/<int:id>/', methods=['GET'])
@auth.login_required
def get_id_comment(id):
    comment = Comments.query.get_or_404(id)
    return jsonify(
        comment.to_json()
    )


@api.route('/courses/<int:id>/comments/', methods=['GET'])
def get_courses_id_comments(id):
    course = Courses.query.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    pagination = course.comment.order_by(desc(Comments.timestamp)).paginate(
        page, per_page=comments_per_page,
        error_out=False
    )
    comments = pagination.items
    prev = ""
    next = ""
    if pagination.has_prev:
        prev = url_for('api.get_courses_id_comments', id=id, page=page - 1)
    if pagination.has_next:
        next = url_for('api.get_courses_id_comments', id=id, page=page + 1)
    comments_count = len(Comments.query.filter_by(course_id=id).all())
    if comments_count % comments_per_page == 0:
        page_count = comments_count//comments_per_page
    else:
        page_count = comments_count//comments_per_page
    last = url_for('api.get_courses_id_comments', id=id, page=page_count)
    return json.dumps(
        [comment.to_json() for comment in comments],
        ensure_ascii=False,
        indent=1
    ), 200, {'link': '<%s>; rel="next", <%s>; rel="last"' % (next, last)}


@api.route('/courses/<int:id>/comments/hot/', methods=["GET"])
def get_hot_comments(id):
    hot_comments = Comments.query.filter_by(
        course_id=id).order_by(Comments.likes).all()
    hot_comments = sorted(hot_comments, key=lambda c: c.likes, reverse=True)
    return json.dumps(
        [comment.to_json() for comment in hot_comments if comment.likes >= 3],
        ensure_ascii=False,
        indent=1
    ), 200


@api.route('/courses/<int:id>/comments/', methods=['POST', 'GET'])
@auth.login_required
def new_comment(id):
    if request.method == 'POST':
        print(request.get_json())
        comment = Comments.from_json(request.get_json())
        comment.user_id = g.current_user.id
        comment.course_id = id
        db.session.add(comment)
        db.session.commit()
        course = Courses.query.get_or_404(id)
        course.count = len(course.comment.all())
        db.session.add(course)
        db.session.commit()
        # add tags ["tag1", "tag2"]
        add_tags(course)
    return jsonify({'id': comment.id}), 201


@api.route('/comments/<int:id>/', methods=["GET", "DELETE"])
@admin_required
def delete_comment(id):
    comment = Comments.query.get_or_404(id)
    course = Courses.query.get_or_404(comment.course_id)
    if request.method == "DELETE":
        db.session.delete(comment)
        db.session.commit()
        course.count = len(course.comment.all())
        db.session.add(course)
        db.session.commit()
        return jsonify({
            'message': '该评论已经被删除'
        })


@api.route('/tip/<int:id>/comments/', methods=['GET'])
def get_tip_id_comments(id):
    tip = Tips.query.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    pagination = tip.comment.order_by(Comments.timestamp).paginate(
        page, per_page=comments_per_page, error_out=False
    )
    comments = pagination.items
    prev = ""
    next = ""
    if pagination.has_prev:
        prev = url_for('api.get_tip_id_comments', id=id, page=page - 1)
    if pagination.has_next:
        next = url_for('api.get_tip_id_comments', id=id, page=page + 1)
    comments_count = len(Comments.query.filter_by(course_id=id).all())
    page_count = comments_count//comments_per_page
    last = url_for('api.get_tip_id_comments', id=id, page=page_count)
    return json.dumps(
        [comment.to_json() for comment in comments],
        ensure_ascii=False,
        indent=1
    ), 200, {'link': '<%s>; rel="next", <%s>; rel="last"' % (next, last)}


@api.route('/tip/<int:id>/comments/', methods=['POST', 'GET'])
@auth.login_required
def new_tip_comment(id):
    comment = Comments.from_json(request.json)
    comment.user_id = g.current_user.id
    comment.tip_id = id
    db.session.add(comment)
    db.session.commit()
    tip = Tips.query.get_or_404(id)
    tip.count = len(tip.comment.all())
    db.session.add(tip)
    db.session.commit()
    return jsonify({'id': comment.id}), 201


@api.route('/tip/<int:tid>/comments/<int:id>/', methods=['DELETE', 'GET'])
@admin_required
def delete_tip_comment(tid, id):
    if request.method == 'DELETE':
        comment = Comments.query.get_or_404(id)
        tip = Tips.query.get_or_404(tid)
        db.session.delete(comment)
        db.session.commit()
        tip.count = len(tip.comment.all())
        db.session.add(tip)
        db.session.commit()
        return jsonify({
            'message': '该评论已经被删除'
        })
