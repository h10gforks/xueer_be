# coding: utf-8

import memcache
from xueer.models import Courses, Tags


memc = memcache.Client(['127.0.0.1:11211'])


def read_data2_memcached():
    courses = Courses.query.all()
    tags = Tags.query.all()
    """
    {
    <courses object>:
        ['teacher', 'name']
    }

    keywords = request.args.get(keywords)
    ----------- search things -------------
    for key in keys: ?
        searchs(search set) = memc.get(key)
        for search in searchs:
            if keywords in search
                return key
    so, how the key loop, but not read data from database
    """

