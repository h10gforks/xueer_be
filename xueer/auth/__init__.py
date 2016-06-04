# -*- coding:utf-8 -*-
"""
    auth
    ````

    : 同步登录模块

"""
from flask import Blueprint


auth = Blueprint('auth', __name__)


from . import views, forms
