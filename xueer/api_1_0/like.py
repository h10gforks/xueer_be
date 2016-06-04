# coding: utf-8
"""
    like.py
    ```````

    : 点赞API

    : login: /api/v1.0/courses/id/like/
    : -- POST: 向特定id的课程点赞
    : -- DELETE: 取消特定id的课程点赞
    : login: /api/v1.0/comments/id/like/
    : -- POST: 向特定id的评论点赞
    : -- DELETE: 取消特定id的评论点赞
    : login: /api/v1.0/tip/id/like/
    : -- POST: 向特定id的tip点赞
    : -- DELETE: 取消特定id的tip点赞
    ......................................

"""
from . import api
from flask import g, jsonify, request
from xueer import db
from xueer.api_1_0.authentication import auth
from xueer.models import Courses, Comments, Tips


@api.route('/courses/<int:id>/like/', methods=["GET", "POST", "DELETE"])
@auth.login_required
def new_courses_id_like(id):
    course = Courses.query.get_or_404(id)
    if request.method == "POST":
        if course.liked:
            return jsonify({
                'error': '你已经点赞过该课程'
            })
        else:
            course.users.append(g.current_user)
            db.session.add(course)
            db.session.commit()
            course.likes = len(course.users.all())
            db.session.add(course)
            db.session.commit()
            course = Courses.query.get_or_404(id)
        return jsonify({
            "likes": course.likes
        }), 201

    elif request.method == "DELETE":
        if course.liked:
            course.users.remove(g.current_user)
            db.session.add(course)
            db.session.commit()
            course.likes = len(course.users.all())
            db.session.add(course)
            db.session.commit()
            course = Courses.query.get_or_404(id)
            return jsonify(
                course.to_json()
            ), 200
        else:
            return jsonify({
                "error": "你还没有点赞这门课程哦!"
            }), 403


@api.route('/comments/<int:id>/like/', methods=["GET", "POST", "DELETE"])
@auth.login_required
def new_comments_id_like(id):
    comment = Comments.query.get_or_404(id)
    if request.method == "POST":
        if comment.liked:
            return jsonify({
                'error': '你已经点赞过该评论'
            })
        else:
            comment.user.append(g.current_user)
            db.session.add(comment)
            db.session.commit()
            comment.likes = len(comment.user.all())
            db.session.add(comment)
            db.session.commit()
            comment = Comments.query.get_or_404(id)
            return jsonify({
              'likes': comment.likes
            }), 201

    elif request.method == "DELETE":
        if comment.liked:
            comment.user.remove(g.current_user)
            db.session.add(comment)
            db.session.commit()
            comment.likes = len(comment.user.all())
            db.session.add(comment)
            db.session.commit()
            comment = Comments.query.get_or_404(id)
            return jsonify(
                comment.to_json()
            ), 200
        else:
            return jsonify({
                "error": "你还没有点赞这个评论哦!"
            }), 403


@api.route('/tip/<int:id>/like/', methods=["GET", "POST", "DELETE"])
@auth.login_required
def new_tips_id_like(id):
    tip = Tips.query.get_or_404(id)
    if request.method == "POST":
        if tip.liked:
            return jsonify({
                'error': '你已经点赞过该贴士'
            })
        else:
            tip.users.append(g.current_user)
            db.session.add(tip)
            db.session.commit()
            tip.likes = len(tip.users.all())
            db.session.add(tip)
            db.session.commit()
            tip = Tips.query.get_or_404(id)
            return jsonify({
                'likes': tip.likes
            }), 201

    elif request.method == "DELETE":
        if tip.liked:
            tip.users.remove(g.current_user)
            db.session.add(tip)
            db.session.commit()
            tip.likes = len(tip.users.all())
            db.session.add(tip)
            db.session.commit()
            tip = Tips.query.get_or_404(id)
            return jsonify(
                tip.to_json()
            ), 200
        else:
            return jsonify({
                "error": "你还没有点赞这个贴士哦!"
            }), 403
