# -*- coding: utf-8 -*-
from app import create_app, db, cli
from app.models import User, Post, Notification, Message, Task

app = create_app()
cli.register(app)


@app.shell_context_processor
def make_shell_context():
    # 将相关的模型添加到 shell 上下文
    return {'db': db, 'User': User, 'Post': Post, 'Message': Message,
            'Notification': Notification, 'Task': Task}
