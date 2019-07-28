import logging
import os
from logging.handlers import SMTPHandler, RotatingFileHandler

from flask import Flask
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from config import Config

app = Flask(__name__)
app.config.from_object(Config)

# flask 插件注册的标准模式

# 数据库再应用的表现形式是一个数据库实例 数据库迁移引擎同样如此
# 它们会在应用实例化之后进行实例化和注册
db = SQLAlchemy(app)
migrate = Migrate(app, db)
# 对 flask-login 插件的
login = LoginManager(app)
login.login_view = 'login'
# flask-login 的常用属性：
# is_authenticated: 一个用来表示用户是否通过登录认证的属性，用True和False表示。
# is_active: 如果用户账户是活跃的，那么这个属性是True，否则就是False
# （译者注：活跃用户的定义是该用户的登录状态是否通过用户名密码登录，通过“记住我”功能保持登录状态的用户是非活跃的）。
# is_anonymous: 常规用户的该属性是False，对特定的匿名用户是True。
# get_id(): 返回用户的唯一id的方法，返回值类型是字符串(Python 2下返回unicode字符串).
mail = Mail(app)

bootstrap = Bootstrap(app)


if not app.debug:

    if app.config['MAIL_SERVER']:
        auth = None
        if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
            auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
        secure = None
        if app.config['MAIL_USE_TLS']:
            secure = ()
        mail_handler = SMTPHandler(
            mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
            fromaddr='no-reply@' + app.config['MAIL_SERVER'],
            toaddrs=app.config['ADMINS'], subject='Microblog Failure',
            credentials=auth, secure=secure)
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)

    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/microblog.log', maxBytes=10240,
                                       backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)

    app.logger.setLevel(logging.INFO)
    app.logger.info('Microblog startup')

from app import routes, models, errors
