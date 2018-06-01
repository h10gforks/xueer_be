# coding: utf-8
"""
    promotion.py
    ```````````

    : 推广模块API
    : -- GET(login) /api/v1.0/promotion/private-promotion-link/: 获取当前登录用户的专属推广链接
    : -- GET /api/v1.0/promotion/top/: 获取当前参与推广活动的用户的推广人数从多到少的排名的用户信息
    ....................................................................

"""
from flask import jsonify, g
from xueer.models import User
from . import api
import json
from xueer.api_1_0.authentication import auth


@api.route('/promotion/private-promotion-link/', methods=['GET'])
@auth.login_required
def promotion_link():
    current_user = User.query.get_or_404(g.current_user.id)
    return jsonify({'private_promotion_link': current_user.generate_private_promotion_link()}), 200


@api.route("/promotion/top/", methods=['GET'])
def get_promotion_top():
    top_list = sorted(User.query.filter(User.recommend_count>0).all(), key=lambda x: x.recommend_count, reverse=True)
    return json.dumps(
        [user.to_json2() for user in top_list],
        ensure_ascii=False,
        indent=1
    ), 200
