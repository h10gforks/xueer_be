# coding: utf-8

import json
from flask import Flask
from flask import render_template,request
from jinja2 import Environment
from . import hello
from xueer.models import Banner, Courses


def is_mobie():
    platform = request.user_agent.platform
    if platform in ["android", "iphone", "ipad"]:
        return True
    else:
        return False


@hello.route('/')
def index():
    flag = is_mobie()
    if flag:
        return render_template("hello/mobile/index.html")
    else:
        banner = Banner.query.all()
        gong_top_list = sorted(Courses.query.filter_by(category_id=1), lambda x: x.count, reverse=True)
        zhuan_top_list = sorted(Courses.query.filter_by(category_id=3), lambda x: x.count, reverse=True)
        tong_top_list = sorted(Courses.query.filter_by(category_id=2), lambda x: x.count, reverse=True)
        su_top_list = sorted(Courses.query.filter_by(category_id=4), lambda x: x.count, reverse=True)
        return render_template("hello/desktop/pages/index.html", banner=banner,
                gong_top_list=gong_top_list, su_top_list=su_top_list
                zhuan_top_list=zhuan_top_list, tong_top_list=tong_top_list
                )

# placehold 路由
@hello.route('/search-result/', methods=['GET'])
def get_search_result():
    """get search result"""
    if is_mobie():
        return render_template("hello/mobile/index.html")
    else:
        return render_template("hello/desktop/pages/search-result.html")


@hello.route('/course/<int:id>/', methods=['GET'])
def course(id):
    """ course index  """
    if is_mobie():
        return render_template("hello/mobile/index.html")
    else:
        return render_template("hello/desktop/pages/index.html")

@hello.route('/tip/<int:id>/', methods=['GET'])
def tip(id):
    """ tip index """
    if is_mobie():
        return render_template("hello/mobile/index.html")
    else:
        return render_template("hello/desktop/index.html")


@hello.route('/courses/', methods=['GET'])
def courses():
    """ get courses """
    if is_mobie():
        return render_template("hello/mobile/index.html")
    else:
        return render_template("hello/desktop/pages/courses.html")


@hello.route('/user/<string:username>/', methods=['GET'])
def user(username):
    """ user index """
    if is_mobie():
        return render_template("hello/mobile/index.html")
    else:
        return render_template("hello/desktop/index.html")


@hello.route('/login/', methods=['GET', 'POST'])
def login():
    """ login """
    if is_mobie():
        return render_template("hello/mobile/index.html")
    else:
        return render_template("hello/desktop/pages/login.html")


@hello.route('/register/', methods=['GET', 'POST'])
def register():
    """ register """
    if is_mobie():
        return render_template("hello/mobile/index.html")
    else:
        return render_template("hello/desktop/pages/register.html")


@hello.route('/category/')
def category():
    """ category """
    if is mobile():
        return render_template("hello/mobile/index.html")
    else:
        return render_template("hello/desktop/pages/category.html")
