from flask import jsonify
from werkzeug.http import HTTP_STATUS_CODES


def error_response(status_code, message=None):
    # 该函数使用来自Werkzeug（Flask的核心依赖项）的HTTP_STATUS_CODES字典，它为每个HTTP状态代码提供一个简短的描述性名称。
    payload = {'error': HTTP_STATUS_CODES.get(status_code, 'Unknown error')}
    if message:
        payload['message'] = message
    response = jsonify(payload)
    # 在创建响应之后，我将状态码设置为对应的错误代码。
    response.status_code = status_code
    return response


def bad_request(message):
    """
    错误请求的响应
    :param message:
    :return:
    """
    error_response(400, message)
