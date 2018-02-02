# coding: utf-8
"""
    question_and_answer.py
    ```````````

    : 问大家模块API
    : -- POST(login) /api/v1.0/course/<id>/create_question/ 向指定课程创建问题，需登录
    : -- DELETE(admin) /api/v1.0/delete_question/<id>/ 删除指定id的问题,管理员操作
    : -- POST(login) /api/v1.0/question/<id>/create_answer/ 向指定问题创建回答，需登录
    : -- DELETE(admin) /api/v1.0/delete_answer/<id>/ 删除指定id的回答
    : -- GET(login) /api/v1.0/course/<id>/questions/ 获取指定课程的所有评论
    : -- GET(login) /api/v1.0/question/<id>/answers/ 获取指定问题的所有回答
    ....................................................................

"""
from flask import request, jsonify,g
from .. import db
from flask_login import login_required, current_user
from ..models import CourseQuestion,Answer,Courses
from . import api
import json
from xueer.api_1_0.authentication import auth
from xueer.decorators import admin_required


@api.route('/course/<int:id>/create_question/', methods=['POST'])
@auth.login_required
def new_question(id):
    """
    向id课程创建新问题
    :param id: 课程id
    :return: 新创建的评论的id和201状态码，对前台起提示左右
    """
    new_question=CourseQuestion(
        question_content= request.get_json().get("question_content"),
        author_id=g.current_user.id,
        course_id=id
    )
    db.session.add(new_question)
    db.session.commit()
    return jsonify({'id': new_question.id}), 201


@api.route("/delete_question/<int:id>/",methods=["DELETE"])
@admin_required
def delete_question(id):
    """
    删除指定id的问题
    :param id:
    :return:
    """
    question = CourseQuestion.query.get_or_404(id)
    db.session.delete(question)
    db.session.commit()
    return jsonify({
        'message': '该问题已经成功删除'
    }),201


@api.route('/question/<int:id>/create_answer/', methods=['POST'])
@auth.login_required
def new_answer(id):
    """
    向id问题创建回答
    :param id: 问题id
    :return: 新创建的问题id和201状态码
    """
    new_answer = Answer(
        answer_content=request.get_json().get("answer_content"),
        author_id=g.current_user.id,
        question_id=id
    )
    db.session.add(new_answer)
    db.session.commit()
    return jsonify({'id': new_answer.id}), 201


@api.route("/delete_answer/<int:id>/", methods=["DELETE"])
@admin_required
def delete_answer(id):
    """
    删除指定id的回答
    :param id: 回答的id
    :return: 提示信息和201
    """
    answer = Answer.query.get_or_404(id)
    db.session.delete(answer)
    db.session.commit()
    return jsonify({
        'message': '该回答已经被成功删除'
    }), 201


@api.route('/course/<int:id>/questions/', methods=['GET'])
@auth.login_required
def get_questions(id):
    """
    获取课程为id的所有提问
    :param id: 课程id
    :return: 新创建的评论的id和201状态码，对前台起提示左右
    """
    course=Courses.query.get_or_404(id)
    questions=course.questions.all()
    return json.dumps(
        [question.to_json() for question in questions],
        ensure_ascii=False,
        indent=1
    ), 200



@api.route('/question/<int:id>/answers/', methods=['GET'])
@auth.login_required
def get_answers(id):
    """
    获取指定问题的所有回答
    :param id: 问题id
    :return:
    """
    question=CourseQuestion.query.get_or_404(id)
    answers=question.answers.all()
    return json.dumps(
        [answer.to_json() for answer in answers],
        ensure_ascii=False,
        indent=1
    ), 200



