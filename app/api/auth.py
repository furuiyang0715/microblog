from flask import g
from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth
from app.api.errors import error_response
from app.models import User

basic_auth = HTTPBasicAuth()
token_auth = HTTPTokenAuth()


@basic_auth.verify_password
def verify_password(username, password):
    """
    验证函数接收客户端提供的用户名和密码，如果凭证有效则返回True，否则返回False。
    :param username:
    :param password:
    :return:
    """
    user = User.query.filter_by(username=username).first()
    if user is None:
        return False
    # 将认证用户保存在g.current_user中，以便我可以从API视图函数中访问它。
    g.current_user = user
    return user.check_password(password)


@basic_auth.error_handler
def basic_auth_error():
    """
    错误处理函数只返回由app/api/errors.py模块中的error_response()函数生成的401错误。
    401错误在HTTP标准中定义为“未授权”错误。
    HTTP客户端知道当它们收到这个错误时，需要重新发送有效的凭证。
    :return:
    """
    return error_response(401)


# 使用verify_token装饰器注册验证函数
@token_auth.verify_token
def verify_token(token):
    """
    验证 token 是否有效
    :param token:
    :return:
    """
    g.current_user = User.check_token(token) if token else None
    # 返回值是 True 还是 False 决定了 Flask-HTTPAuth 是否允许视图函数的运行
    return g.current_user is not None


@token_auth.error_handler
def token_auth_error():
    return error_response(401)
