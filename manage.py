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
    CourseCategories, CoursesSubCategories, CourseTypes, Comments, Teachers, \
    Tags, Tips, CourseQuestion, Answer

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
                     CoursesSubCategories=CoursesSubCategories,
                     CourseTypes=CourseTypes, Comments=Comments,
                     Teachers=Teachers, Tags=Tags, Tips=Tips,
                     CourseQuestion=CourseQuestion, Answer=Answer)
    return shell_ctx


manager.add_command('shell', Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)


@manager.command
def test(coverage=False):
    """Run the unit tests."""
    import sys
    if coverage and not os.environ.get('XUEER_COVERAGE'):
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
    sys.exit(0)


@manager.command
def adduser():
    name = raw_input('Username> ')
    email = raw_input('Email> ')
    input_password = getpass('Password> ')
    role = input('Role(2:admin, 3:user)> ')

    password = base64.b64encode(input_password)
    new = User(name=name, email=email,
               password=password, role_id=role)
    db.session.add(new)
    db.session.commit()
    print "new user <%s> created" % name


@manager.command
def set_score():
    # All imports
    import math
    import jieba
    from jieba import posseg as pseg
    from xueer.sentiment_score.emo_list import pos_list
    from xueer.sentiment_score.emo_list import neg_list

    # Load user's dictionary
    dict_dir = './xueer/sentiment_score/dict.txt'
    jieba.load_userdict(dict_dir)

    # Get courses and set scores
    courses = Courses.query.filter_by(available=True).all()

    def listToUnicode(target):
        """Convert words into unicode for matching"""
        count = 0
        while (count < len(target)):
            target[count] = unicode(target[count])
            count += 1
        return target

    listToUnicode(pos_list)
    listToUnicode(neg_list)

    def parse_comment(comment):
        dismiss = ['b', 'c', 'r', 'uj', 'u', 'p', 'q', 'uz', 't', 'ul', 'k',
                   'f', 'ud', 'ug', 'uv']
        parsed = []
        pseg_cut = pseg.cut(comment.body)
        for word, flag in pseg_cut:
            if flag not in dismiss:
                parsed.append(word)
        return parsed

    def get_count(comment_parsed):
        """
        Count positive and negative words in a comment parsed list
        """
        pos_count = 0
        neg_count = 0
        for word in comment_parsed:
            if word in pos_list:
                pos_count += 1
            elif word in neg_list:
                neg_count += 1
            elif '80' <= word <= '99':
                pos_count += 1
            elif '0' <= word < '80':
                neg_count += 1
        return pos_count, neg_count

    def get_emotion(pos_count, neg_count):
        """
        Get comment emotion according to positive and negtive words' quantity
        """
        # Theta Matrix
        theta = [-0.33276, 0.94999, -0.25728]
        x = [1, float(pos_count), float(neg_count)]
        feature_sum = 0
        for i in range(3):
            feature_sum += theta[i] * x[i]
        hypothesis = 1 / (1 + math.e ** -(feature_sum))

        if 0 < hypothesis < 0.4:
            emotion = 0.0
        elif 0.4 <= hypothesis < 0.6:
            emotion = 0.5
        elif 0.6 <= hypothesis < 1:
            emotion = 1.0
        return emotion

    def get_score(course):
        """Get score of a course by comments"""
        comments = course.comment.all()

        # No comment on this course, set to 0
        score = 0

        if len(comments) > 0:
            for comment in comments:
                comment_parsed = parse_comment(comment)
                pos_count, neg_count = get_count(comment_parsed)
                emotion = get_emotion(pos_count, neg_count)
                if emotion == 1.0:
                    score += 1
                elif emotion == 0.0:
                    score -= 1
                elif emotion == 0.5:
                    pass
        return score

    for course in courses:
        course.score = get_score(course)
        db.session.add(course)
        print "Course <{cid}> scored: {score}".format(cid=course.id, score=course.score)
    db.session.commit()


if __name__ == '__main__':
    if sys.argv[1] == 'test' or sys.argv[1] == 'lint':
        os.environ['XUEER_CONFIG'] = 'testing'
    manager.run()
