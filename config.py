# -*- coding: utf-8 -*-
import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = ['your-email@example.com']
    # 国际化支持的语言列表
    # en 为英文
    # es 为西班牙语言
    # zh 为中文
    LANGUAGES = ['en', 'es', 'zh']
    # 微软的翻译服务
    MS_TRANSLATOR_KEY = os.environ.get('MS_TRANSLATOR_KEY')
    # 有道的翻译服务
    YOUDAO_URL = os.environ.get("YOUDAO_URL")
    YOUDAO_APP_KEY = os.environ.get("YOUDAO_APP_KEY")
    YOUDAO_APP_SECRET = os.environ.get("YOUDAO_APP_SECRET")

    POSTS_PER_PAGE = 25

    ELASTICSEARCH_URL = os.environ.get('ELASTICSEARCH_URL')

    # 在程序中指定 http://www.bjhee.com/flask-ext3.html
    #  应用默认语言，不设置的话即为 en
    BABEL_DEFAULT_LOCALE = "zh"
    # 应用默认时区，不设置的话即为UTC
    # BABEL_DEFAULT_TIMEZONE="UTC"
