# coding: utf-8
"""
    admin
    `````

    : 学而管理后台
    ...............

    : copyright: (c) 2016 by MuxiStudio
    : license: MIT
"""

from flask import Blueprint


admin = Blueprint('admin', __name__)


from . import views
