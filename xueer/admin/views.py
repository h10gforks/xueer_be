# coding: utf-8
"""
    views.py
    ````````

    : admin views
    ..............

    : copyright: (c) 2016 by MuxiStudio
    : license: MIT

"""

from . import admin
from flask import render_template
from flask_login import login_required


@admin.route('/')
@login_required
def index():
    return render_template("admin/index.html")
