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
        seller['id'] = data["uid"][0]
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
            seller['name'] = el[0].text_content().strip()

        el = page.cssselect(".main-title .user .user-rating")
        if el:
            seller['rating'] = el[0].text_content().strip()

        el = page.cssselect(".feedbacksSummary table")
        if el:
            seller['info'] = parser.html(el[0])

    except:
        error = dict(reason=u"Не удалось найти информацию о продавце", details=u"Нет нужной информации на странице")
        return render_template("seller.html", error=error)

    return render_template("seller.html", seller=seller)

@core.route("/ajax/item/")
def ajax_item():
    link = request.args.get("link", "")
    result = {}

    # init parser
    parser = Parser(charset="utf-8")

    #request item page
    try:
        page = parser.grab(link)
    except:
        error = dict(reason=u"Не удалось найти страницу товара", details=u"Неправильная ссылка или нет связи с сервером")
        return jsonify(error=error)

    try:
        el = page.cssselect("meta[itemprop='name']")
        if el:
            result['name'] = el[0].get("content")

        el = page.cssselect("meta[itemprop='price']")
        if el:
            result['price'] = el[0].get("content")

        el = page.cssselect("meta[itemprop='priceCurrency']")
        if el:
            result['currency'] = el[0].get("content")

    except:
        error = dict(reason=u"Не удалось найти информацию о товаре", details=u"Нет нужной информации на странице")
        return jsonify(error=error)

    return jsonify(result=result)

@core.route("/ajax/seller/<int:id>/list/<int:count>/")
def ajax_seller_list(id, count=9999):
    page_number = 1
    result = []

    # init parser
    parser = Parser(charset="utf-8")

    while len(result) < count:
        #request seller info page
        try:
            page = parser.grab("http://aukro.ua/show_user.php?uid=%s&type=fb_seller&p=%s" % (id, page_number))
        except:
            error = dict(reason=u"Не удалось загрузить список", details=u"Нет связи с сервером")
            return jsonify(error=error)

        try:
            for el in page.cssselect(".feedbacks-row"):
                cols = el.cssselect("td")

                if cols and len(cols) >= 4:
                    data = dict(datetime=cols[2].text_content().strip(),
                                item=cols[3].text_content().strip(),
                                link=cols[3].cssselect("a")[0].get("href"))

                    result.append(data)

        except:
            pass

        if page.cssselect(".pagination li.next"):
            page_number += 1
        else:
            break

    return jsonify(result=result)
