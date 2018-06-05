# coding: utf-8
"""
    question_and_answer.py
    ```````````

    : 问大家模块API
    : -- POST(login) /api/v1.0/course/<id>/question/ 向指定课程创建问题，需登录
    : -- DELETE(admin) /api/v1.0/question/<id>/ 删除指定id的问题,管理员操作
    : -- POST(login) /api/v1.0/question/<id>/answer/ 向指定问题创建回答，需登录
    : -- DELETE(admin) /api/v1.0/answer/<id>/ 删除指定id的回答
    : -- GET(login) /api/v1.0/course/<id>/questions/ 获取指定课程的所有提问
    : -- GET(login) /api/v1.0/question/<id>/answers/ 获取指定问题的所有回答
    : -- GET(admin) /api/v1.0/questions/ 分页获取所有问题
    : -- GET(admin) /api/v1.0/answers/ 分页获取所有回答
    ....................................................................

"""
from flask import request, jsonify,g,url_for
from .. import db
from flask_login import login_required, current_user
from ..models import CourseQuestion,Answer,Courses
from . import api
import json
from sqlalchemy import desc
from xueer.api_1_0.authentication import auth
from xueer.decorators import admin_required,moderator_required


questions_per_page = 20
answers_per_page = 20


@api.route('/course/<int:id>/question/', methods=['POST'])
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


@api.route("/question/<int:id>/",methods=["DELETE"])
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


@api.route('/question/<int:id>/answer/', methods=['POST'])
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


@api.route("/answer/<int:id>/", methods=["DELETE"])
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



@api.route('/questions/', methods=["GET"])
@moderator_required
def get_pagination_questions():
    """
    获取所有问题，支持分页
    """
    page = request.args.get('page', 1, type=int)
    pagination = CourseQuestion.query.order_by(desc(CourseQuestion.create_time)).paginate(
        page, per_page=questions_per_page, error_out=False
    )
    questions = pagination.items
    prev = ""
    next = ""
    if pagination.has_prev:
        prev = url_for('api.get_pagination_questions', page=page - 1)
    if pagination.has_next:
        next = url_for('api.get_pagination_questions', page=page + 1)
    questions_count = len(CourseQuestion.query.all())
    if questions_count % questions_per_page == 0:
        page_count = questions_count//questions_per_page
    else:
        page_count = questions_count//questions_per_page
    last = url_for('api.get_pagination_questions', page=page_count)
    return json.dumps(
        [q.to_json() for q in questions],
        ensure_ascii=False,
        indent=1
    ), 200, {'link': '<%s>; rel="next", <%s>; rel="last"' % (next, last)}



@api.route('/answers/', methods=["GET"])
@moderator_required
def get_pagination_answers():
    """
    获取所有回答，支持分页
    """
    page = request.args.get('page', 1, type=int)
    pagination = Answer.query.order_by(desc(Answer.create_time)).paginate(
        page, per_page=answers_per_page, error_out=False
    )
    answers = pagination.items
    prev = ""
    next = ""
    if pagination.has_prev:
        prev = url_for('api.get_pagination_answers', page=page - 1)
    if pagination.has_next:
        next = url_for('api.get_pagination_answers', page=page + 1)
    answers_count = len(Answer.query.all())
    if answers_count % answers_per_page == 0:
        page_count = answers_count//answers_per_page
    else:
        page_count = answers_count//answers_per_page
    last = url_for('api.get_pagination_answers', page=page_count)
    return json.dumps(
        [answer.to_json() for answer in answers],
        ensure_ascii=False,
        indent=1
    ), 200, {'link': '<%s>; rel="next", <%s>; rel="last"' % (next, last)}
