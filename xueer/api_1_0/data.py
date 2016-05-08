# coding: utf-8
from flask import request
from . import api
from xueer.decorators import admin_required
from xueer.models import Courses

@api.route('/courses/<int:id>/data', methods=["GET", "PUT"])
@admin_required
def put_course_get_data(id):
    """
    更新一门课
    """
    course = Courses.query.get_or_404(id)
    if request.method == "PUT":
        data_dict = eval(request.data)
    return "request data: %r" % request.data
 
