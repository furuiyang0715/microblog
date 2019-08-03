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

    POSTS_PER_PAGE = 10

    # ELASTICSEARCH_URL = os.environ.get('ELASTICSEARCH_URL', None)
    ELASTICSEARCH_URL = None
    BABEL_DEFAULT_LOCALE = "zh"

    # 七牛云存储的AccessKey/SecretKey
    QINIU_ACCESS_KEY = "odFMFZXhkObsy3hHJ9SvFMFkiIa6DJxb3GOBXjSg"
    QINIU_SECRET_KEY = "rCbbUAP6Taaq10XZZrAyGWxTk5d-nu0GSItbgjwz"

    # 要上传的七牛云空间
    QINIU_BUCKET_NAME = "furuiyang-microblog"


