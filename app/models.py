# -*- coding: utf-8 -*-
import base64
import json
import os
from datetime import datetime, timedelta
from hashlib import md5
from time import time

import redis
import rq
from flask import current_app, url_for
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from app import db, login
from app.search import query_index, add_to_index, remove_from_index

followers = db.Table(
    'followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)


class PaginatedAPIMixin(object):
    @staticmethod
    def to_collection_dict(query, page, per_page, endpoint, **kwargs):
        """
        query page 和 per_page 是 Flask-SQLAlchemy查询对象 页码 以及每页的数据数量
        这三个参数决定了要返回的参数是什么
        :param query:
        :param page:
        :param per_page:
        :param endpoint: 根据该值决定需要发送到 url_for 的视图函数
        :param kwargs: endpoint 路由的更多参数
        :return:
        """
        resources = query.paginate(page, per_page, False)
        data = {
            'items': [item.to_dict() for item in resources.items],
            '_meta': {
                'page': page,
                'per_page': per_page,
                'total_pages': resources.pages,
                'total_items': resources.total
            },
            '_links': {
                'self': url_for(endpoint, page=page, per_page=per_page,
                                **kwargs),
                'next': url_for(endpoint, page=page + 1, per_page=per_page,
                                **kwargs) if resources.has_next else None,
                'prev': url_for(endpoint, page=page - 1, per_page=per_page,
                                **kwargs) if resources.has_prev else None
            }
        }
        return data


class User(PaginatedAPIMixin, UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    followed = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')
    # 添加一个新模型来跟踪所有用户的用户的通知以及用户模型中的关系
    notifications = db.relationship('Notification', backref='user',
                                    lazy='dynamic')

    # 发出的私信
    messages_sent = db.relationship('Message',
                                    foreign_keys='Message.sender_id',
                                    backref='author', lazy='dynamic')
    # 收到的私信
    messages_received = db.relationship('Message',
                                        foreign_keys='Message.recipient_id',
                                        backref='recipient', lazy='dynamic')
    # 用户最后一次阅读自己私有消息的时间
    last_message_read_time = db.Column(db.DateTime)

    tasks = db.relationship('Task', backref='user', lazy='dynamic')

    # 用户 token 以及用户 token 的过期时间
    token = db.Column(db.String(32), index=True, unique=True)
    token_expiration = db.Column(db.DateTime)

    # 查询最新私信的数量
    def new_messages(self):
        last_read_time = self.last_message_read_time or datetime(1900, 1, 1)
        return Message.query.filter_by(recipient=self).filter(
            Message.timestamp > last_read_time).count()

    # 处理通知对象
    # 为用户添加通知给数据库
    # 确保如果有相同的通知存在 则会首先删除该通知
    def add_notification(self, name, data):
        self.notifications.filter_by(name=name).delete()
        n = Notification(name=name, payload_json=json.dumps(data), user=self,
                         timestamp=time()
                         )
        db.session.add(n)
        return n

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user):
        return self.followed.filter(
            followers.c.followed_id == user.id).count() > 0

    def followed_posts(self):
        followed = Post.query.join(
            followers, (followers.c.followed_id == Post.user_id)).filter(
                followers.c.follower_id == self.id)
        own = Post.query.filter_by(user_id=self.id)
        return followed.union(own).order_by(Post.timestamp.desc())

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            current_app.config['SECRET_KEY'],
            algorithm='HS256').decode('utf-8')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)

    def launch_task(self, name, description, *args, **kwargs):
        """
        负责将任务提交到 RQ 队列 并将其添加到数据库中
        :param name: 函数名称
        :param description:
        :param args:
        :param kwargs:
        :return:
        """
        # 构建符合规范的函数名称并且使用队列的 enqueue 来提交作业以及相关参数
        rq_job = current_app.task_queue.enqueue('app.tasks.' + name, self.id,
                                                *args, **kwargs)
        # descirption 是呈现给用户的任务的友好描述
        task = Task(id=rq_job.get_id(), name=name, description=description,
                    user=self)
        # 添加会话但是暂时不发生提交行为
        # 一般来说，最好在更高层次函数中的数据库会话上进行操作，因为它允许你在单个事务中组合由较低级别函数所做的多个更新
        # 这不是一个严格的规则
        db.session.add(task)
        return task

    def get_tasks_in_progress(self):
        """
        返回用户未完成任务的列表
        :return:
        """
        return Task.query.filter_by(user=self, complete=False).all()

    def get_task_in_progress(self, name):
        """
        确定前一个任务是否还在运行
        :param name:
        :return:
        """
        return Task.query.filter_by(name=name, user=self,
                                    complete=False).first()

    def to_dict(self, include_email=False):
        """
        将用户信息封装成一个 json 字典
        之后会被转换为 json 传输
        :param include_email: 只有用户请求自己的数据时才包含点电子邮件
        :return:
        """
        data = {
            'id': self.id,
            'username': self.username,
            # 对于时间 将使用 ISO 8601 格式
            # Python的datetime对象可以通过isoformat()方法生成这样格式的字符串。
            # 但是因为我使用的datetime对象的时区是UTC，且但没有在其状态中记录时区，
            # 所以我需要在末尾添加Z，即ISO 8601的UTC时区代码。
            'last_seen': self.last_seen.isoformat() + 'Z',   # 上次访问时间
            'about_me': self.about_me,
            'post_count': self.posts.count(),
            'follower_count': self.followers.count(),
            'followed_count': self.followed.count(),
            '_links': {
                'self': url_for('api.get_user', id=self.id),
                'followers': url_for('api.get_followers', id=self.id),
                'followed': url_for('api.get_followed', id=self.id),
                # TODO 头像暂时是 应用外部的Gravatar URL
                'avatar': self.avatar(128)
            }
        }
        if include_email:
            data['email'] = self.email
        return data

    def from_dict(self, data, new_user=False):
        """
        实现从 python 字典向 User 对象的转换
        :param data:
        :param new_user:
        :return:
        """

        for field in ['username', 'email', 'about_me']:
            if field in data:
                # 在对象相应的属性中设置新值
                setattr(self, field, data[field])
        if new_user and 'password' in data:
            # password 不是对象中的字段
            # 调用 set_password 来创建密码哈希
            self.set_password(data['password'])

    def get_token(self, expires_in=3600):
        now = datetime.utcnow()
        # token 未过期的情况
        if self.token and self.token_expiration > now + timedelta(seconds=60):
            return self.token
        # 重新生成 token
        self.token = base64.b64encode(os.urandom(24)).decode('utf-8')
        # 重新设置 token 的过期时间 通常为生成时间之后 3600 s
        self.token_expiration = now + timedelta(seconds=expires_in)
        db.session.add(self)
        return self.token

    def revoke_token(self):
        # 使分配给用户的 token 失效
        self.token_expiration = datetime.utcnow() - timedelta(seconds=1)

    @staticmethod
    def check_token(token):
        """
        它将一个token作为参数传入并返回此token所属的用户。 如果token无效或过期，则该方法返回None。
        :param token:
        :return:
        """
        user = User.query.filter_by(token=token).first()
        if user is None or user.token_expiration < datetime.utcnow():
            return None
        return user


# 用户通知类
class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), index=True)  # 名称
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # 关联用户
    timestamp = db.Column(db.Float, index=True, default=time)  # 时间戳 TODO 没有设置成功
    payload_json = db.Column(db.Text)  # 有效荷载

    def get_data(self):
        return json.loads(str(self.payload_json))


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class SearchableMixin(object):
    @classmethod
    def search(cls, expression, page, per_page):
        ids, total = query_index(cls.__tablename__, expression, page, per_page)
        if total == 0:
            # 使用数据库进行模糊查询
            # return cls.query.filter_by(id=0), 0
            posts = list(cls.query.filter(cls.body.like("%" + expression + "%")).order_by(cls.id))
            total = len(posts)
            return posts, total

        when = []
        for i in range(len(ids)):
            when.append((ids[i], i))
        return cls.query.filter(cls.id.in_(ids)).order_by(
            db.case(when, value=cls.id)), total

    @classmethod
    def before_commit(cls, session):
        session._changes = {
            'add': [obj for obj in session.new if isinstance(obj, cls)],
            'update': [obj for obj in session.dirty if isinstance(obj, cls)],
            'delete': [obj for obj in session.deleted if isinstance(obj, cls)]
        }

    @classmethod
    def after_commit(cls, session):
        for obj in session._changes['add']:
            add_to_index(cls.__tablename__, obj)
        for obj in session._changes['update']:
            add_to_index(cls.__tablename__, obj)
        for obj in session._changes['delete']:
            remove_from_index(cls.__tablename__, obj)
        session._changes = None

    @classmethod
    def reindex(cls):
        for obj in cls.query:
            add_to_index(cls.__tablename__, obj)


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    def __repr__(self):
        return '<Message {}>'.format(self.body)


class Post(SearchableMixin, db.Model):
    __searchable__ = ['body']
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    language = db.Column(db.String(5))

    def __repr__(self):
        return '<Post {}>'.format(self.body)


class Task(db.Model):
    # 使用由RQ生成的作业标识符作主键
    # 存储的是符合命名规范的名称（会传递给 RQ），
    # 适应于向用户显示的任务描述，该任务所属的用户关系以及任务是否已经完成的布尔值
    id = db.Column(db.String(36), primary_key=True)
    name = db.Column(db.String(128), index=True)
    description = db.Column(db.String(128))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    # 将正在运行的任务与已经完成的任务分开 运行中的任务需要特殊处理才能显示最新进度
    complete = db.Column(db.Boolean, default=False)

    def get_rq_job(self):
        """
        get_rq_job()辅助方法可以用给定的任务ID加载RQJob实例
        :return:
        """
        try:
            # 从 redis 中存在的数据中加载 Job 实例
            rq_job = rq.job.Job.fetch(self.id, connection=current_app.redis)
        except (redis.exceptions.RedisError, rq.exceptions.NoSuchJobError):
            return None
        return rq_job

    def get_progress(self):
        """
        建立在 get_job() 之上 返回任务的进度百分比
        在这里我们假设：
        （1） 如果模型中的作业 ID 不存在于 RQ 队列中 则表示作业已经完成并且数据已经过期并已经从队列中删除
             在这种情况下返回的 百分比为 100%
        （2） 如果job 存在，但是meta 属性中找不到进度相关的信息，我们安全地假定该 job 计划运行，但是还没有启动。
             在这种情况下返回的 百分比为 0.
        :return:
        """
        job = self.get_rq_job()
        return job.meta.get('progress', 0) if job is not None else 100


# 添加监听
db.event.listen(db.session, 'before_commit', Post.before_commit)
db.event.listen(db.session, 'after_commit', Post.after_commit)

# 使用 Post 的 reindex() 来初始化当前在数据库中的所有用户动态的索引
# Post.reindex()
