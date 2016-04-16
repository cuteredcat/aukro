#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This is aukro config file
# Do not change this file, use instance/aukro.conf instead

HOST = "localhost"
PORT = 5000

BASE_URL = "http://localhost:5000"

DEBUG = True
TESTING = False

SECRET_KEY = "DuMmY sEcReT kEy"

CSRF_ENABLED = True
CSRF_SESSION_KEY = "_csrf_token"

MONGODB_SETTINGS = {
    "db": "aukro",
    "host": "mongodb://localhost"
}

BABEL_DEFAULT_LOCALE = "ru"
BABEL_DEFAULT_TIMEZONE = "Europe/Kiev"

# Google Analytics
GA_UA = "UA-XXXXXXXX-X"
