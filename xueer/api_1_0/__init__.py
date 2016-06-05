# coding: utf-8
"""
    api
    ```

    : 学而后台 API 模块
    ...................

    : copyright: (c) 2016 by MuxiStudio
    : license: MIT
"""

from flask import Blueprint


api = Blueprint('api', __name__)


from . import authentication, comments, courses, errors, register,\
    tags, teachers, tips, users, like, category, sure, search,\
    memcached, statistics
