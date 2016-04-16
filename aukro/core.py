#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Blueprint, jsonify, render_template, request, url_for

from aukro import app, db

# create blueprint
core = Blueprint("core", __name__, template_folder="templates")

@core.route("/")
def index():
    if request.is_xhr:
        return jsonify()
    else:
        return render_template("index.html")
