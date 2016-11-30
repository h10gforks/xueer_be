# coding: utf-8
"""
    manage.py
    ~~~~~~~~~

    : [intro]
    : -- xueer backend management

    : [shell]
      -- python manage.py db init
      -- python manage.py db migrate
      -- python manage.py db upgrade
      -- python manage.py runserver
      -- python manage.py test
      -- python manage.py adduser (username) (email)
      -- python manage.py freeze

"""
import os
COV = None
if os.environ.get('XUEER_COVERAGE'):
    import coverage
    COV = coverage.coverage(branch=True, include='xueer/*')
    COV.start()

import sys
import base64
from getpass import getpass

from xueer import app, db
from flask import g
from flask_script import Manager, Shell
from flask_migrate import Migrate, MigrateCommand
from xueer.models import Permission, Role, User, AnonymousUser, Courses, \
    CourseCategories, CourseTypes, Comments, Teachers, Tags, Tips


# set encoding to utf-8
# but reload is evil:)
reload(sys)
sys.setdefaultencoding('utf-8')


manager = Manager(app)
migrate = Migrate(app, db)


def make_shell_context():
    shell_ctx = dict(app=app, db=db, Permission=Permission, Role=Role,
                     User=User, AnonymousUser=AnonymousUser, Courses=Courses,
                     g=g, CourseCategories=CourseCategories,
                     CourseTypes=CourseTypes, Comments=Comments,
                     Teachers=Teachers, Tags=Tags, Tips=Tips)
    return shell_ctx
manager.add_command('shell', Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)


@manager.command
def test(coverage=False):
    """Run the unit tests."""
    if coverage and not os.environ.get('XUEER_COVERAGE'):
        import sys
        os.environ['XUEER_COVERAGE'] = '1'
        os.execvp(sys.executable, [sys.executable] + sys.argv)
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)
    if COV:
        COV.stop()
        COV.save()
        print('Coverage Summary:')
        COV.report()
        COV.erase()


@manager.command
def adduser():
    name = raw_input('Username> ')
    email = raw_input('Email> ')
    input_password = getpass('Password> ')
    role = input('Role(2:admin, 3:user)> ')

    password = base64.b64encode(input_password)
    new = User(name=name, email=email,
               password=password, role=role)
    db.session.add(new)
    db.session.commit()
    print "new user <{name}> created".format(name)


@manager.command
def emoAnalysis():
    import jieba
    from xueer.emo_list import pos_list
    from xueer.emo_list import neg_list

    # 将词典中数据项转换成unicode, 便于与jieba分词的结果相匹配
    def listToUnicode(target):
        """change encoding of a list to unicode"""
        count = 0
        while(count<len(target)):
            target[count] = unicode(target[count])
            count += 1
        return target
    listToUnicode(pos_list)
    listToUnicode(neg_list)

    # 加载自定义词频的词典
    cur_dir_list = os.getcwd().split('/')
    cur_dir_list.append('xueer/dict.txt')
    dict_dir = '/'.join(cur_dir_list)
    jieba.load_userdict(dict_dir)

    # 获取所有课程及其评论，通过分析评论的文本获取情感分析的分数
    courses = Courses.query.filter_by(available=True).all()

    for course in courses:
        course.score = 0
        print 'Checking on Class %d' % course.id,
        comments = course.comment.all()
        if len(comments) != 0:
            for comment in comments:
                seg_list = jieba.cut(comment.body, cut_all=False)
                for each_seg in seg_list:
                    if each_seg in pos_list:
                        course.score += 1
                    elif each_seg in neg_list:
                        course.score -= 1
        course.score += course.likes*0.1
        print '  done.'
    print 'All Done!'


if __name__ == '__main__':
    if sys.argv[1] == 'test' or sys.argv[1] == 'lint':
        os.environ['XUEER_CONFIG'] = 'test'
    manager.run()
