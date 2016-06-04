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
import sys
import base64
from getpass import getpass

from xueer import create_app, db
from flask import g
from flask_script import Manager, Shell
from flask_migrate import Migrate, MigrateCommand
from xueer.models import Permission, Role, User, AnonymousUser, Courses, \
    CourseCategories, CourseTypes, Comments, Teachers, Tags, Tips


# set encoding to utf-8
# but reload is evil:)
reload(sys)
sys.setdefaultencoding('utf-8')


app = create_app(os.getenv('XUEER_CONFIG') or 'default')
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


if __name__ == '__main__':
    if sys.argv[1] == 'test' or sys.argv[1] == 'lint':
        os.environ['XUEER_CONFIG'] = 'test'
    manager.run()
