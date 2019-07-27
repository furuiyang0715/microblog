from app import app
from flask import render_template, flash, redirect

from app.form import LoginForm


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
    form = LoginForm()
    if form.validate_on_submit():  # 将执行表单的校验工作 全部成功返回 True 有失败的就返回 False
        # 调用 flash 的时候 会将消息存储在 flask 中 但是不会显示出来
        # 一旦通过get_flashed_messages函数请求了一次，它们就会从消息列表中移除，所以在调用flash()函数后它们只会出现一次。
        flash('Login requested for user {}, remember_me={}'.format(
            form.username.data, form.remember_me.data))
        return redirect('/index')
    return render_template('login.html', title='Sign In', form=form)
