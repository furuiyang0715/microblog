from flask import Flask
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


from app import routes, models
