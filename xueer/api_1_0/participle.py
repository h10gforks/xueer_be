# coding: utf-8
"""
    participle.py
    `````````````

    jieba分词模块
    :copyright: (c) 2016 by MuxiStudio
    :license: MIT
"""

import jieba
from xueer import db
from xueer.models import Courses, Search
from . import api


def participle(course):
    """
    分词处理函数
    :param course: 分词课程
    :return: 添加分词、课程对应关系
    """
    generator = jieba.cut_for_search(course.name)
    seg_list = '/'.join(generator)
    results = seg_list.split('/')
    results.append(course.name)
    for seg in results:
        if not Search.query.filter_by(name=seg).first():
            search = Search(name=seg)
            search.courses.append(course)
        else:
            search = Search.query.filter_by(name=seg).first()
            search.courses.append(course)
        db.session.add(search)
        db.session.commit()


@api.route('/participle/')
def start_participle():
    """
    分词触发函数
    :param: None
    :return: 对当前数据库中的所有课程进行分词
    """
    courses = Courses.query.all()
    print '---------- start participle ------------'
    for course in courses:
        # 所有课程进行分词
        print course.__repr__(), '....... done!'
        participle(course)
    print '---------- participle done! ------------'
