# coding: utf-8

import json
from flask import Flask
from flask import render_template,request
from jinja2 import Environment
from . import hello
from xueer.models import Courses, Tips, Tags, CourseCategories, CourseTag


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
        tips = sorted(Tips.query.all(), key=lambda x: x.id, reverse=True)[:3]
        gong_list = Courses.query.filter_by(category_id=1).all()
        gong_top_list = sorted(gong_list, key=lambda x: x.count, reverse=True)[:3]
        zhuan_top_list = sorted(Courses.query.filter_by(category_id=3).all(), key=lambda x: x.count, reverse=True)[:3]
        tong_top_list = sorted(Courses.query.filter_by(category_id=2).all(), key=lambda x:x.count, reverse=True)[:3]
        su_top_list = sorted(Courses.query.filter_by(category_id=4).all(), key=lambda x:x.count, reverse=True)[:3]
        # hot_five = sorted(Courses.query.all)
        return render_template(
            "hello/desktop/pages/index.html", tips=tips,
            gong_top_list=gong_top_list, su_top_list=su_top_list,
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
        info = Courses.query.get_or_404(id)
        info_tags = []
        for course_tag in info.tags.all():
            info_tags.append(Tags.query.get_or_404(course_tag.tag_id))
        category = {
            1: "公", 2: "通", 3: "专", 4: "素"
        }.get(info.category_id)
        hot_comments = []; comments = []
        return render_template(
            "hello/desktop/pages/courses.html",
            info = info, category = category,
            info_tags = info_tags,
            hot_comments = hot_comments,
            comments = comments,
            hot_comments_len = len(hot_comments),
            comments_len = len(comments)
        )


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
    if is_mobie():
        return render_template("hello/mobile/index.html")
    else:
        hot_tags = sorted(Tags.query.all(), key=lambda tag: tag.count, reverse=True)[:12]
        return render_template(
            "hello/desktop/pages/category.html",
            hot_tags = hot_tags
        )
