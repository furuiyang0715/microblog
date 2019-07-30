import logging
from logging.handlers import SMTPHandler, RotatingFileHandler
import os

from elasticsearch import Elasticsearch
from flask import Flask, request, current_app
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_babel import Babel, lazy_gettext as _l
from config import Config

db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = 'auth.login'
login.login_message = _l('Please log in to access this page.')
mail = Mail()
bootstrap = Bootstrap()
moment = Moment()
babel = Babel()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    mail.init_app(app)
    bootstrap.init_app(app)
    moment.init_app(app)
    babel.init_app(app)

    # 添加一个 es 的实例
    # Python 对象在结构上并不严格 可以随时添加新属性
    app.elasticsearch = Elasticsearch([app.config['ELASTICSEARCH_URL']]) \
        if app.config['ELASTICSEARCH_URL'] else None

    from app.errors import bp as errors_bp
    app.register_blueprint(errors_bp)

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    if not app.debug and not app.testing:
        if app.config['MAIL_SERVER']:
            auth = None
            if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
                auth = (app.config['MAIL_USERNAME'],
                        app.config['MAIL_PASSWORD'])
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
        file_handler = RotatingFileHandler('logs/microblog.log',
                                           maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s '
            '[in %(pathname)s:%(lineno)d]'))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info('Microblog startup')

    return app


@babel.localeselector
def get_locale():
    # Babel实例提供了一个localeselector装饰器。 为每个请求调用装饰器函数以选择用于该请求的语言
    # 这里我使用了Flask中request对象的属性accept_languages。 request对象提供了一个高级接口，
    # 用于处理客户端发送的带Accept-Language头部的请求。 该头部指定了客户端语言和区域设置首选项。
    # 该头部的内容可以在浏览器的首选项页面中配置，默认情况下通常从计算机操作系统的语言设置中导入。
    # 大多数人甚至不知道存在这样的设置，但是这是有用的，因为应用可以根据每个语言的权重，提供优选语言的列表。
    # 下面是一个复杂的Accept-Languages头部的例子： Accept-Language: da, en-gb;q=0.8, en;q=0.7
    # 要选择最佳语言，你需要将客户请求的语言列表与应用支持的语言进行比较，并使用客户端提供的权重，查找最佳语言。
    # 这样做的逻辑有点复杂，但它已经全部封装在best_match()方法中了，
    # 该方法将应用提供的语言列表作为参数并返回最佳选择。
    # test_language = request.accept_languages.best_match(current_app.config['LANGUAGES'])
    # print("===================")
    # print(test_language)   # en
    # print("===================")

    # TODO 临时替换为 中文
    return 'zh'

    # return request.accept_languages.best_match(current_app.config['LANGUAGES'])


from app import models