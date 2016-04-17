#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Blueprint, jsonify, render_template, request, url_for

from aukro import app, db
from aukro.parser import Parser

import re

# create blueprint
core = Blueprint("core", __name__, template_folder="templates")

@core.route("/")
def index():
    return render_template("index.html")

@core.route("/seller/")
def seller():
    search = request.args.get("search", "")
    seller = {}

    # init parser
    parser = Parser(charset="utf-8")

    # try to find seller id
    data = parser.data(search)
    if data and "uid" in data:
        seller['id'] = data["uid"]
    else:
        try:
            page = parser.grab(search, tree=False)
        except:
            error = dict(reason=u"Не удалось найти продавца", details=u"Неправильная ссылка или нет связи с сервером")
            return render_template("seller.html", error=error)

        result = re.search("data-seller=[\"\']([0-9]+)[\"\']", page, flags=re.I | re.M)
        if result and result.group(1):
            seller['id']= result.group(1)
        else:
            error = dict(reason=u"Не удалось найти продавца", details=u"Неправильная ссылка")
            return render_template("seller.html", error=error)

    #request seller info page
    try:
        page = parser.grab("http://aukro.ua/show_user.php?uid=%s&type=fb_seller" % seller['id'])
    except:
        error = dict(reason=u"Не удалось найти информацию о продавце", details=u"Нет связи с сервером")
        return render_template("seller.html", error=error)

    try:
        el = page.cssselect(".main-title .user .uname")
        if el:
            seller['name'] = u" ".join(el[0].xpath("./text()")).strip()

        el = page.cssselect(".main-title .user .user-rating")
        if el:
            seller['rating'] = u" ".join(el[0].xpath("./text()")).strip()

        el = page.cssselect(".feedbacksSummary table")
        if el:
            seller['info'] = parser.tostring(el[0])

    except:
        error = dict(reason=u"Не удалось найти информацию о продавце", details=u"Нет нужной информации на странице")
        return render_template("seller.html", error=error)

    return render_template("seller.html", seller=seller)

@core.route("/ajax/seller/<int:id>/list/<int:count>/")
def ajax_seller_list(id, count=9999):
    result = []
    page = 1

    # init parser
    parser = Parser(charset="utf-8")

    while len(result) < count:
        #request seller info page
        try:
            page = parser.grab("http://aukro.ua/show_user.php?uid=%s&type=fb_seller&p=%s" % (id, page))
        except:
            error = dict(reason=u"Не удалось загрузить список", details=u"Нет связи с сервером")
            return jsonify(error=error)

        try:
            for el in page.cssselect(".feedbacks-row"):
                rows = el.cssselect("td")

                if rows and len(rows) >= 4:
                    data = dict(datetime=u" ".join(rows[3].xpath("./text()")).strip(),
                                type=u" ".join(rows[2].xpath("./text()")).strip(),
                                item=u" ".join(rows[4].xpath("./text()")).strip(),
                                link=rows[4].cssselect("a")[0].get("href"))

                    result.append(data)

        except:
            pass

        if page.cssselect(".pagination li.next"):
            page += 1
        else:
            break

    return jsonify(result=result)
