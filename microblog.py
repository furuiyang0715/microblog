from app import app, db
from app.models import User, Post


# 通过添加数据库实例和一个模型实例来创建一个 shell 上下文环境
# 当启动 shell 的时候 就会调用这个函数并且在 shell 会话中注册它返回的项目
# 函数返回一个字典而不是一个列表，原因是对于每个项目，你必须通过字典的键提供一个名称以便在shell中被调用。
@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Post': Post}
