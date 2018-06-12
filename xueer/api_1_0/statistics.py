# coding: utf-8
"""
    statistics.py
    `````````````

    : 全站部分状态API

    : GET(admin) /api/v1.0/statistics/: 显示部分集合状态
    ....................................................

"""

from . import api
from xueer.decorators import admin_required,moderator_required
from xueer.models import Comments
from xueer.models import User
from xueer.models import Courses
from flask import jsonify


@api.route('/statistics/', methods=["GET"])
@moderator_required
def get_statistics():
    comments_count = len(Comments.query.all())
    users_count = len(User.query.all())
    courses_count = len(Courses.query.all())
    return jsonify({
        'comments_count': comments_count,
        'users_count': users_count,
        'courses_count': courses_count
    }), 200


# 获取从该id往后新增的用户数
@api.route('/statistics/user/<int:uid>/', methods = ['GET'])
@moderator_required
def get_user_added(uid):
    user_all = User.query.all()
    count = 0
    for user in user_all:
        if user.id > uid:
            count = count + 1
    return jsonify({
            "user_added": count
        }), 200

# date格式: YYYY-MM-DD 如 2018-06-01
@api.route('/statistics/comment/<string:date>/', methods = ['GET'])
@moderator_required
def get_comment_added(date):
    comment_all = Comments.query.all()
    year, month, day = map(int, date.split('-'))
    comment_added = 0
    for comment in comment_all:
        ctime = comment.timestamp
        # 将2018-01-01 12:22:01 中的year, month, day 拿出来
        cyear, cmonth, cday = map(int, str(ctime).split(' ')[0].split('-'))
        f = lambda cyear, cmonth, cday: (cyear > year or cyear == year) and (cmonth > month or cmonth == month) and (cday > day or cday == day)
        if f(cyear, cmonth, cday):
            comment_added = comment_added + 1
    print("comment_added:", comment_added)
    return jsonify({
            "comment_added": comment_added            
        }), 200
