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
