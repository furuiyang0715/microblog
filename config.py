# -*- coding: utf-8 -*-
import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.flaskenv'))


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'furuiyang'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    # MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USE_SSL = True
    MAIL_USE_TLS = False
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = ['15626046299@163.com']
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

    # Redis连接URL将来自环境变量，如果该变量未定义，
    # 则会假定该服务在当前主机的默认端口上运行并使用默认URL。
    REDIS_URL = os.environ.get('REDIS_URL') or 'redis://47.107.180.248:6379'
    # REDIS_URL = os.environ.get('REDIS_URL') or 'redis://127.0.0.1:6379'

    # 是否在控制台显示日志
    LOG_TO_STDOUT = True



