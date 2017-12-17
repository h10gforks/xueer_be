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
from flask import render_template, redirect, url_for
from flask_login import login_required, current_user

@admin.route('/')
def index():
    if not current_user.is_administrator():
        return redirect(url_for('auth.login'))
    return render_template("admin/index.html")
