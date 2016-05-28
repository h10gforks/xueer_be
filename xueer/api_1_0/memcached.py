# coding: utf-8

from xueer.decorators import admin_required
from xueer.models import Courses, Tags
from xueer import lru
from . import api
from flask import jsonify, request


def read_data2_memcached():
    """
    将postgresql数据库中的课程搜索数据
    读入LRU并写入硬盘(数据库读取开销)
    """
    courses = Courses.query.all()
    for course in courses:
       lru.set(course.to_json(), [course.name, course.teacher])
    lru.save()  # 数据存储硬盘


def update_course_memcached(id):
    """
    更新特定id课程的缓存
    """
    course = Courses.query.get_or_404(id)
    lru.delete(course)
    lru.set(course.to_json(), [course.name, course.teacher])
    lru.save()


def delete_course_memcached(id):
    """
    删除特定课程的缓存(课程被删除后自动执行)
    """
    course = Courses.query.get_or_404(id)
    lru.delete(course)
    lru.save()


@api.route('/memcached/', methods=['GET', 'POST'])
# @admin_required
def memcached():
    """
    将录课数据读入缓存
    """
    if request.method == 'POST':
        lru.flushdb()
        read_data2_memcached()
        return jsonify({
            'set_memcached': '1'
        })


@api.route('/memcached/<int:id>/', methods=['GET', 'POST'])
@admin_required
def memcached_course(id):
    """
    更新特定课程的缓存
    """
    if request.method == 'POST':
        update_course_memcached(id)
        return jsonify({
            'update_memcached': '1'
        })


@api.route('/memcached/<int:id>/', methods=['GET', 'DELETE'])
@admin_required
def delete_memcached_course(id):
    """
    删除特定课程的缓存数据
    """
    if request.method == 'DELETE':
        delete_course_memcached(id)
        return jsonify({
            'delete_memcached': '1'
        })
