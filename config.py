import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    # 增加 SQLite 数据库的配置
    # sqlite 数据库比较轻量级
    # 每个数据库都存在磁盘上的单个文件上面
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                              'sqlite:///' + os.path.join(basedir, 'app.db')
    # 设置数据库发生变更时是否发送消息给应用
    SQLALCHEMY_TRACK_MODIFICATIONS = False
