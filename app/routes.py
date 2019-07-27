from flask_login import current_user, login_user

from app import app
from flask import render_template, flash, redirect, url_for

from app.form import LoginForm
from app.models import User


@app.route("/") 
@app.route("/index")
def index():
    user = {'username': 'Miguel'}
    posts = [
        {
            'author': {'username': 'John'},
            'body': 'Beautiful day in Portland!'
        },
        {
            'author': {'username': 'Susan'},
            'body': 'The Avengers movie was so cool!'
        }
    ]
    return render_template('index.html', title='Home', user=user, posts=posts)


@app.route('/login', methods=['GET', 'POST'])
def login():
    # current_user 是 通过 load user 加载到的一个当前用户对象
    # 这个变量的值可以是数据库中的一个用户对象（Flask-Login通过我上面提供的用户加载函数回调读取），
    # 或者如果用户还没有登录，则是一个特殊的匿名用户对象。
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():

        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)
