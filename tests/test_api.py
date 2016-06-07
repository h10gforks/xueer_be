# coding: utf-8
import unittest
import json
import re
from base64 import b64encode
from flask import url_for
from xueer import create_app, db
from xueer.models import User, Role, Courses, Comments


class APITestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app.config.update(
            SERVER_NAME='myapp.dev:5000'
        )
        self.app.testing = True
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        Role.insert_roles()
        self.client = self.app.test_client()


    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()


    def get_api_headers(self, username, password):
        return {
            'Authorization': 'Basic ' + b64encode(
                (username + ':' + password).encode('utf-8')
            ).decode('utf-8'),
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }


    def get_token_headers(self, token):
        return {
            'Authorization': 'Basic ' + b64encode((token+':')),
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }


    def test_admin_token(self):
        u = User(
            email = 'admin@admin.com',
            username = 'admin',
            password = b64encode('muxi304'),
            role_id = 2
        )
        db.session.add(u)
        db.session.commit()

        user_token_json = self.client.get(
            url_for('api.get_token'),
            headers = self.get_api_headers(
                'admin@admin.com', 'muxi304'
            )
        )
        user_token = eval(user_token_json.data).get('token')
        u = User.query.filter_by(email='admin@admin.com').first()
        expect_token = u.generate_auth_token()
        self.assertTrue(str(user_token) == str(expect_token))

        res = self.client.get(
            url_for('api.get_comments'),
            headers = self.get_token_headers(user_token)
        )
        self.assertTrue(res.status_code == 200)


    def test_normal_token(self):
        u = User(
            email = 'neo1218@yeah.net',
            password = b64encode('muxi304'),
            role_id = 3
        )
        db.session.add(u)
        db.session.commit()
        token = u.generate_auth_token()

        res = self.client.get(
            url_for('api.get_comments'),
            headers = self.get_token_headers(token)
        )
        self.assertTrue(res.status_code == 403)


    def test_404(self):
        res = self.client.get(
            '/wrong/url',
            headers = self.get_api_headers('email', 'password')
        )
        self.assertTrue(res.status_code == 404)


    def test_no_auth(self):
        res = self.client.get(url_for('api.get_courses'),
            content_type='application/json'
        )
        self.assertTrue(res.status_code == 200)


    # def test_bad_auth(self):
    #     r = Role.query.filter_by(name='User').first()
    #     self.assertIsNotNone(r)
    #     u = User(
    #         email='neo1218@yeah.net',
    #         password=b64encode('muxi304'),
    #         role_id=3
    #     )
    #     db.session.add(u)
    #     db.session.commit()

    #     res = self.client.get(
    #         url_for('api.get_comments'),
    #         headers=self.get_api_headers(
    #             'neo1218@yeah.net', 'muxi304'
    #         )
    #     )
    #     self.assertTrue(res.status_code == 401)


