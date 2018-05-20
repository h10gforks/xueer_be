# coding: utf-8
"""
    test_api.py
    ```````````
    : api 功能测试

"""

import unittest
import json
import re
from base64 import b64encode
from flask import url_for
from xueer import create_app, db
from xueer.models import Tips
from xueer.models import CourseQuestion, Answer,Tags
from xueer.api_1_0.kmp import kmp
from flask import abort
from flask_sqlalchemy import SQLAlchemy
from xueer.models import User, Role, Courses, Comments,CourseCategories,CoursesSubCategories,CourseTypes

class APITestCase(unittest.TestCase):
    def setUp(self):
        """
        初始化测试
        """
        print("SETUP...............")
        self.app = create_app("testing")
        self.app.config.update(
            SERVER_NAME='localhost:5000',
            debug=False
        )
        self.app.testing = True
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        Role.insert_roles()
        # CourseTypes.generate_fake()
        # CourseCategories.generate_fake()
        # CoursesSubCategories.generate_fake()
        # User.generate_fake()
        # Courses.generate_fake()
        # Tips.generate_fake()
        # Comments.generate_fake()
        # CourseQuestion.generate_fake()
        # Answer.generate_fake()
        # Tags.generate_fake()
        self.client = self.app.test_client()

    def tearDown(self):
        """
        测试结束, 清空环境
        """
        print("TEARDOWN...................")
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def get_api_headers(self, username, password):
        """
        username:password headers
        """
        return {
            'Authorization': 'Basic ' + b64encode(
                (username + ':' + password).encode('utf-8')
            ).decode('utf-8'),
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

    def get_token_headers(self, token):
        """
        token headers
        """
        return {
            'Authorization': 'Basic ' + b64encode((token + ':')),
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

    def test_admin_token(self):
        """
        测试管理员token
        """
        u = User(
            email='admin@admin.com',
            username='admin',
            password=b64encode('muxi304'),
            role_id=2
        )
        db.session.add(u)
        db.session.commit()

        user_token_json = self.client.get(
            url_for('api.get_token'),
            headers=self.get_api_headers(
                'admin@admin.com', 'muxi304'
            )
        )
        user_token = eval(user_token_json.data).get('token')
        u = User.query.filter_by(email='admin@admin.com').first()
        expect_token = u.generate_auth_token()
        self.assertTrue(str(user_token) == str(expect_token))

        res = self.client.get(
            url_for('api.get_comments'),
            headers=self.get_token_headers(user_token)
        )
        self.assertTrue(res.status_code == 200)

    def test_normal_token(self):
        """
        测试普通用户token
        """
        u = User(
            email='neo1218@yeah.net',
            password=b64encode('muxi304'),
            role_id=3
        )
        db.session.add(u)
        db.session.commit()
        token = u.generate_auth_token()

        res = self.client.get(
            url_for('api.get_comments'),
            headers=self.get_token_headers(token)
        )
        self.assertTrue(res.status_code == 403)

    def test_404(self):
        """
        测试404 json响应
        """
        res = self.client.get(
            '/wrong/url',
            headers=self.get_api_headers('email', 'password')
        )
        self.assertTrue(res.status_code == 404)

    def test_401(self):
        """
        测试401 json响应
        """
        res = self.client.get(url_for('api.get_comments'))
        self.assertTrue(res.status_code == 401)

    def test_500(self):
        """
        测试500 json响应
        """
        res = self.client.get(url_for('api.get_token'),
                              headers=self.get_api_headers('email', 'username')
                              )
        self.assertTrue(res.status_code == 500)

    def test_no_auth(self):
        """
        测试无token限制的资源
        """
        res = self.client.get(url_for('api.get_courses'),
                              content_type='application/json'
                              )
        self.assertTrue(res.status_code == 200)

    def test_tip_page(self):
        """
        测试首页: 管理员创建tip, 用户阅读tip
        """
        u = User(
            email='admin@admin.com',
            username='admin',
            password=b64encode('muxi304'),
            role_id=2
        )
        db.session.add(u)
        db.session.commit()
        admin_token = u.generate_auth_token()

        res = self.client.post(url_for('api.new_tip'),
                               headers=self.get_token_headers(admin_token),
                               data=json.dumps({
                                   'title': 'test tips',
                                   'img_url': 'http://substack.net/images/rov.png',
                                   'body': 'this is a test tip body, enen',
                                   'author': 'test app'
                               })
                               )
        self.assertTrue(res.status_code == 201)

        res = self.client.get(url_for('api.get_tip_id', id=1),
                              content_type='application/json'
                              )
        self.assertTrue(res.status_code == 200)

    def test_like_tip(self):
        """
        测试给相应tip点赞
        """
        u = User(
            email='admin@admin.com',
            username='admin',
            password=b64encode('muxi304'),
            role_id=2
        )
        db.session.add(u)
        db.session.commit()
        admin_token = u.generate_auth_token()

        res = self.client.post(url_for('api.new_tip'),
                               headers=self.get_token_headers(admin_token),
                               data=json.dumps({
                                   'title': 'test tips',
                                   'img_url': 'http://substack.net/images/rov.png',
                                   'body': 'this is a test tip body, enen',
                                   'author': 'test app'
                               })
                               )

        res = self.client.post(url_for('api.new_tips_id_like', id=1),
                               headers=self.get_token_headers(admin_token)
                               )
        likes = Tips.query.get_or_404(1).likes
        self.assertTrue(likes == 1)

        res = self.client.post(url_for('api.new_tips_id_like', id=1),
                               headers=self.get_token_headers(admin_token)
                               )
        self.assertTrue(res.status_code == 403)

        res = self.client.delete(url_for('api.new_tips_id_like', id=1),
                                 headers=self.get_token_headers(admin_token)
                                 )
        likes = Tips.query.get_or_404(1).likes
        self.assertTrue(likes == 0)

        res = self.client.delete(url_for('api.new_tips_id_like', id=1),
                                 headers=self.get_token_headers(admin_token)
                                 )
        self.assertTrue(res.status_code == 403)

    def test_create_course(self):
        """
        测试管理员创建课程
        """
        u = User(
            email='neo1218@yeah.net',
            username='neo1218',
            password=b64encode('muxi304'),
            role_id=2
        )
        db.session.add(u)
        db.session.commit()
        token = u.generate_auth_token()

        res = self.client.post(url_for('api.new_course'),
                               headers=self.get_token_headers(token),
                               data=json.dumps({
                                   'name': 'test course',
                                   'teacher': 'test teacher',
                                   'category_id': 1,
                                   'type_id': 1,
                               })
                               )
        self.assertTrue(res.status_code == 201)

    def test_write_course_comment(self):
        """
        测试编写课程评论
        """
        u = User(
            email='neo1218@yeah.net',
            username='neo1218',
            password=b64encode('muxi304'),
            role_id=2
        )
        db.session.add(u)
        db.session.commit()
        token = u.generate_auth_token()

        res = self.client.post(url_for('api.new_course'),
                               headers=self.get_token_headers(token),
                               data=json.dumps({
                                   'name': 'test course',
                                   'teacher': 'test teacher',
                                   'category_id': 1,
                                   'type_id': 1,
                               })
                               )

        res = self.client.post(url_for('api.new_comment', id=1),
                               headers=self.get_token_headers(token),
                               data=json.dumps({
                                   'body': 'this is a test comment',
                                   'tags': ''
                               })
                               )
        self.assertTrue(res.status_code == 201)

    def test_like_comment(self):
        """
        测试给相应的评论点赞
        """
        u = User(
            email='admin@admin.com',
            username='admin',
            password=b64encode('muxi304'),
            role_id=2
        )
        db.session.add(u)
        db.session.commit()
        admin_token = u.generate_auth_token()

        res = self.client.post(url_for('api.new_course'),
                               headers=self.get_token_headers(admin_token),
                               data=json.dumps({
                                   'name': 'test course',
                                   'teacher': 'test teacher',
                                   'category_id': 1,
                                   'type_id': 1,
                               })
                               )

        res = self.client.post(url_for('api.new_comment', id=1),
                               headers=self.get_token_headers(admin_token),
                               data=json.dumps({
                                   'body': 'this is a test comment',
                                   'tags': ''
                               })
                               )

        res = self.client.post(url_for('api.new_comments_id_like', id=1),
                               headers=self.get_token_headers(admin_token)
                               )
        likes = Comments.query.get_or_404(1).likes
        self.assertTrue(likes == 1)

        res = self.client.post(url_for('api.new_comments_id_like', id=1),
                               headers=self.get_token_headers(admin_token)
                               )
        self.assertTrue(res.status_code == 403)

        res = self.client.delete(url_for('api.new_comments_id_like', id=1),
                                 headers=self.get_token_headers(admin_token)
                                 )
        likes = Comments.query.get_or_404(1).likes
        self.assertTrue(likes == 0)

        res = self.client.delete(url_for('api.new_comments_id_like', id=1),
                                 headers=self.get_token_headers(admin_token)
                                 )
        self.assertTrue(res.status_code == 403)

    def test_like_course(self):
        """
        测试给相应课程点赞
        """
        u = User(
            email='admin@admin.com',
            username='admin',
            password=b64encode('muxi304'),
            role_id=2
        )
        db.session.add(u)
        db.session.commit()
        admin_token = u.generate_auth_token()

        res = self.client.post(url_for('api.new_course'),
                               headers=self.get_token_headers(admin_token),
                               data=json.dumps({
                                   'name': 'test course',
                                   'teacher': 'test teacher',
                                   'category_id': 1,
                                   'type_id': 1
                               })
                               )

        res = self.client.post(url_for('api.new_courses_id_like', id=1),
                               headers=self.get_token_headers(admin_token)
                               )
        likes = Courses.query.get_or_404(1).likes
        self.assertTrue(likes == 1)

        res = self.client.post(url_for('api.new_courses_id_like', id=1),
                               headers=self.get_token_headers(admin_token)
                               )
        self.assertTrue(res.status_code == 403)

        res = self.client.delete(url_for('api.new_courses_id_like', id=1),
                                 headers=self.get_token_headers(admin_token)
                                 )
        likes = Courses.query.get_or_404(1).likes
        self.assertTrue(likes == 0)

        res = self.client.delete(url_for('api.new_courses_id_like', id=1),
                                 headers=self.get_token_headers(admin_token)
                                 )
        self.assertTrue(res.status_code == 403)

    def test_kmp(self):
        target_string = "this is a target string"
        pattern_string = " i"
        result = kmp(target_string, pattern_string)
        self.assertTrue(result == 4)

        pattern_string = "haha"
        result = kmp(target_string, pattern_string)
        self.assertTrue(result == False)

    def test_create_and_delete_question(self):
        """
        测试向特定课程提问和删除问题
        """
        u = User(
            email='andrew@gmail.com',
            username='andrew',
            password=b64encode('muxi304'),
            role_id=2
        )
        db.session.add(u)
        db.session.commit()
        token = u.generate_auth_token()

        res = self.client.post(url_for('api.new_course'),
                               headers=self.get_token_headers(token),
                               data=json.dumps({
                                   'name': 'test course',
                                   'teacher': 'test teacher',
                                   'category_id': 1,
                                   'type_id': 1,
                               })
                               )

        res1 = self.client.post(url_for('api.new_question', id=1),
                                headers=self.get_token_headers(token),
                                data=json.dumps({
                                    'question_content': 'this is a test question'
                                })
                                )
        self.assertTrue(res1.status_code == 201)

        res2 = self.client.delete(url_for('api.delete_question', id=1),
                                  headers=self.get_token_headers(token),
                                  data=json.dumps({}))
        self.assertTrue(res2.status_code == 201)

    def test_create_and_delete_answer(self):
        """
        测试向指定提问回答和删除回答
        """
        u = User(
            email='andrew@gmail.com',
            username='andrew',
            password=b64encode('muxi304'),
            role_id=2
        )
        db.session.add(u)
        db.session.commit()
        token = u.generate_auth_token()

        res = self.client.post(url_for('api.new_course'),
                               headers=self.get_token_headers(token),
                               data=json.dumps({
                                   'name': 'test course',
                                   'teacher': 'test teacher',
                                   'category_id': 1,
                                   'type_id': 1,
                               })
                               )

        res = self.client.post(url_for('api.new_question', id=1),
                               headers=self.get_token_headers(token),
                               data=json.dumps({
                                   'question_content': 'this is a test question'
                               })
                               )

        res1 = self.client.post(url_for('api.new_answer', id=1),
                                headers=self.get_token_headers(token),
                                data=json.dumps({
                                    'answer_content': 'this is a test answer'
                                })
                                )
        self.assertTrue(res1.status_code == 201)

        res2 = self.client.delete(url_for('api.delete_answer', id=1),
                                  headers=self.get_token_headers(token),
                                  data=json.dumps({})
                                  )
        self.assertTrue(res2.status_code == 201)

    def test_get_questions_and_get_answers(self):
        """
        测试获得特定课程的所有问题
        """
        u = User(
            email='andrew@gmail.com',
            username='andrew',
            password=b64encode('muxi304'),
            role_id=2
        )
        db.session.add(u)
        db.session.commit()
        token = u.generate_auth_token()

        res = self.client.post(url_for('api.new_course'),
                               headers=self.get_token_headers(token),
                               data=json.dumps({
                                   'name': 'test course',
                                   'teacher': 'test teacher',
                                   'category_id': 1,
                                   'type_id': 1,
                               })
                               )

        res = self.client.post(url_for('api.new_question', id=1),
                               headers=self.get_token_headers(token),
                               data=json.dumps({
                                   'question_content': 'this is a test question'
                               })
                               )
        res = self.client.post(url_for('api.new_answer', id=1),
                               headers=self.get_token_headers(token),
                               data=json.dumps({
                                   'answer_content': 'this is a test answer'
                               })
                               )
        res1 = self.client.get(url_for("api.get_questions", id=1),
                               headers=self.get_token_headers(token),
                               data=json.dumps({}))
        self.assertTrue(res1.status_code == 200)

        res2 = self.client.get(url_for("api.get_answers", id=1),
                               headers=self.get_token_headers(token),
                               data=json.dumps({}))
        self.assertTrue(res2.status_code == 200)
