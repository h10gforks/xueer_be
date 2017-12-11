# -*- coding:utf-8 -*-
"""
    hello
    `````

    : 学而桌面版同步接口模块

"""
from flask import Blueprint


hello = Blueprint('hello', __name__)


from . import views
from ..models import Permission


@hello.app_context_processor
def inject_permissions():
    return dict(Permission=Permission)
