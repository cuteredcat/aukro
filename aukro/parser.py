#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime
from lxml.html import fromstring, make_links_absolute
from urlparse import parse_qs, urlparse

import cookielib, json, importlib, re, urllib, urllib2

RE_URL = re.compile(r"""(?i)\b((?:[a-z][\w-]+:(?:/{1,3}|[a-z0-9%])|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’]))""")

class HTTPRedirectHandler(urllib2.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        newreq = urllib2.HTTPRedirectHandler.redirect_request(self, req, fp, code, msg, headers, newurl)
        if newreq is not None: self.redirections.append(newreq.get_full_url())
        return newreq

class Parser():
    def __init__(self, charset='cp1251', *args, **kwargs):
        self.charset = charset
        self.cookie = cookielib.CookieJar()

        self.headers = [('User-agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.93 Safari/537.36'),
                        ('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8')]

    def link(self, link):
        if isinstance(link, unicode):
            link = link.encode('utf-8')

        if re.match(RE_URL, link):
            return link

        return None

    def data(self, link):
        link = self.link(link)

        if link:
            return parse_qs(urlparse(link).query, keep_blank_values=True)
        else:
            return None

    def grab(self, link, tree=True):
        try:
            opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookie))
            opener.addheaders = self.headers

            link = self.link(link)
            socket = opener.open(link)

            if self.charset is None:
                content = socket.read()
            else:
                content = unicode(socket.read(), self.charset)

            socket.close()

        except:
            content = None

        if content and tree:
            content = make_links_absolute(fromstring(content), link, resolve_base_href=True)

        return content
