# coding: utf-8

"""
  sure.py
  ~~~~~~~
    根据邮箱确定用户是否存在

"""

from xueer.decorators import admin_required
from xueer.models import User
from . import api
from flask import request, jsonify


@api.route('/check_email/', methods=["GET", "POST"])
def check_email():
    if request.method == "POST":
        email = request.get_json().get('email')
        user = User.query.filter_by(email=email).first()
        if user:
            return jsonify({
              "user": "true"
            })
        else:
            return jsonify({"user": "false"})


@api.route('/check_username/', methods=['GET', 'POST'])
def check_username():
    if request.method == "POST":
        username= request.get_json().get('username')
        user = User.query.filter_by(username=username).first()
        if user:
            return jsonify({
              "user": "true"
            })
        else:
            return jsonify({"user": "false"})
