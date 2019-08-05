import json
import sys
import time


# 一个简单的后台任务示例:
# def example(seconds):
#     print("Starting task")
#     for i in range(seconds):
#         print(i)
#         time.sleep(1)
#     print("Task completed")


# 带有进度的后台任务示例:
import time

from flask import render_template
from rq import get_current_job

# 不同与一个简单的任务 发送邮件需要用到应用中的一些功能 例如说访问数据库以及发送电子邮件
# 因为这将在单独的进程中运行，所以我需要初始化Flask-SQLAlchemy和Flask-Mail，
# 而Flask-Mail又需要Flask应用实例以从中获取它们的配置。
# 因此，将在app/tasks.py模块的顶部添加Flask应用实例和应用上下文：
from app import create_app, db
from app.email import send_email
from app.models import Task, User, Post

app = create_app()
# 推送一个上下文使用成为当前应用的实例
# 这样一来Flask-SQLAlchemy等插件才可以使用current_app.config 获取它们的配置。
# 没有上下文，current_app表达式会返回一个错误。
app.app_context().push()


def example(seconds):
    """
    可以报告任务进度的的示例后台任务
    :param seconds:
    :return:
    """
    # 获取一个作业示例
    job = get_current_job()
    print("Starting task")
    for i in range(seconds):
        # 作业对象的meta属性是一个字典，任务可以编写任何想要与应用程序通信的自定义数据
        # 在此例中 写入了 process 表示作业任务的进度 即完成任务的百分比
        job.meta['process'] = 100.0 * i / seconds
        # 每次更新该属性数据的时候 就调用 save_meta 将数据写入 redis
        job.save_meta()
        print(i)
        time.sleep(1)
    job.meta['process'] = 100
    job.save_meta()
    print("Task completed")


def _set_task_progress(progress):
    job = get_current_job()
    if job:
        # 将任务进度写入 job.meta 字典并保存到 redis 中
        job.meta['progress'] = progress
        job.save_meta()
        task = Task.query.get(job.get_id())
        # 生成一个通知
        task.user.add_notification('task_progress', {'task_id': job.get_id(),
                                                     'progress': progress})
        if progress >= 100:
            task.complete = True
        db.session.commit()


def export_posts(user_id):
    """
    实现导出用户任务
    :param user_id:
    :return:
    """
    try:
        # read user posts from database
        user = User.query.get(user_id)
        _set_task_progress(0)
        data = []
        i = 0
        total_posts = user.posts.count()
        for post in user.posts.order_by(Post.timestamp.asc()):
            # 包含正文以及动态发表的时间
            data.append({'body': post.body,
                         'timestamp': post.timestamp.isoformat() + 'Z'})
            # 延长导出的时间 以便在用户动态不多的情况下 也可以观察到导出进度的增长
            time.sleep(5)
            i += 1
            _set_task_progress(100 * i // total_posts)
        # send email with data to user
        send_email('[Microblog] Your blog posts',
                   sender=app.config['ADMINS'][0], recipients=[user.email],
                   text_body=render_template('email/export_posts.txt', user=user),
                   html_body=render_template('email/export_posts.html', user=user),
                   attachments=[('posts.json', 'application/json',
                                 json.dumps({'posts': data}, indent=4))],
                   sync=True)
    except:
        # handle unexpected errors
        _set_task_progress(100)
        app.logger.error('Unhandled exception', exc_info=sys.exc_info())
