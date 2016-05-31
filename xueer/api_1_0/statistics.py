# coding: utf-8

from . import api
from xueer.decorators import admin_required
from xueer.models import Comments
from xueer.models import User
from xueer.models import Courses
from flask import jsonify


@api.route('/statistics/', methods=["GET"])
@admin_required
def get_statistics():
    comments_count = len(Comments.query.all())
    users_count = len(User.query.all())
    courses_count = len(Courses.query.all())
    return jsonify({
        'comments_count': comments_count,
        'users_count': users_count,
        'courses_count': courses_count
    }), 200
