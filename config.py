# -*- coding: utf-8 -*-
import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'furuiyang'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = ['your-email@example.com']
    LANGUAGES = ['en', 'es', 'zh']
    MS_TRANSLATOR_KEY = os.environ.get('MS_TRANSLATOR_KEY')
    YOUDAO_URL = os.environ.get("YOUDAO_URL")
    YOUDAO_APP_KEY = os.environ.get("YOUDAO_APP_KEY")
    YOUDAO_APP_SECRET = os.environ.get("YOUDAO_APP_SECRET")

    POSTS_PER_PAGE = 3

    ELASTICSEARCH_URL = os.environ.get('ELASTICSEARCH_URL')
    BABEL_DEFAULT_LOCALE = "zh"

