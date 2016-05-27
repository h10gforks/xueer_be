# coding: utf-8
"""
    search.py
    `````````

    xueer search api
"""

from . import api
import memcache


@api.route('/search/', methods=['GET'])
def search():
    """
    搜索API
    """
    keywords = request.args.get('keywords')
