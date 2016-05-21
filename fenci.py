# coding: utf-8
"""
    fenci.py
    ````````

    学而课程分词脚本
"""

import requests
from xueer.models import Courses
import base64

token=base64.b64encode('eyJpZCI6MX0.32BFm_OeqXXn558zOr2t9queYDc:')
print token

Headers = {
            'host': 'xueer.ccnuer.cn',
            'connection': 'keep-alive',
            'authorization':"Basic %s" % token,
            'accept': '*/*',
            'accept-encoding': 'gzip, deflate',
            'User-Agent': 'Mozilla/5.0(Windows NT 10.0; WOW64)'
         }

for course in Courses.query.all():
        id=course.id
        data={
                'name':course.name,
                'teacher':course.teacher,
                'category_id':course.category_id,
                'sub_category_id':course.subcategory_id,
                'type_id':course.type_id
              }
        r=requests.put(
            'http://xueer.ccnuer.cn/api/v1.0/courses/%s/' % str(id),data=str(data),headers=Headers
        )
        print r.status_code
        print id
