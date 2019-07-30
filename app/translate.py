# -*- coding: utf-8 -*-
import hashlib
import json
import time
import uuid

import requests
from flask import current_app
from flask_babel import _


# def translate(text, source_language, dest_language):
#     """
#     使用 微软 的 api
#     :param text:
#     :param source_language:
#     :param dest_language:
#     :return:
#     """
#     if 'MS_TRANSLATOR_KEY' not in current_app.config or \
#             not current_app.config['MS_TRANSLATOR_KEY']:
#         return _('Error: the translation service is not configured.')
#     auth = {
#         'Ocp-Apim-Subscription-Key': current_app.config['MS_TRANSLATOR_KEY']}
#     r = requests.get('https://api.microsofttranslator.com/v2/Ajax.svc'
#                      '/Translate?text={}&from={}&to={}'.format(
#                          text, source_language, dest_language),
#                      headers=auth)
#     if r.status_code != 200:
#         return _('Error: the translation service failed.')
#     return json.loads(r.content.decode('utf-8-sig'))


def encrypt(signStr):
    hash_algorithm = hashlib.sha256()
    hash_algorithm.update(signStr.encode('utf-8'))
    return hash_algorithm.hexdigest()


def truncate(q):
    """
    对要翻译的文本进行截断
    :param q:
    :return:
    """
    if q is None:
        return None
    size = len(q)
    # 在小于 20 的时候返回要翻译的原文
    # 在大于 20 的时候返回前 10 个 + 后面 10 个
    return q if size <= 20 else q[0:10] + str(size) + q[size - 10:size]


def do_request(data):
    """
    将请求发送到翻译 api
    :param data:
    :return:
    """
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    return requests.post(current_app.config['YOUDAO_URL'], data=data, headers=headers)


def translate(text, source_language, dest_language):
    """
    使用有道的 api 进行翻译
    :param text:
    :param source_language:
    :param dest_language:
    :return:
    """
    if 'YOUDAO_APP_KEY' not in current_app.config or \
            not current_app.config['YOUDAO_APP_KEY']:
        return _('Error: the translation service is not configured.')
    # 构造请求数据
    data = dict()
    data['from'] = "zh-CHS" if source_language == "zh" else source_language
    data['to'] = "zh-CHS" if dest_language == "zh" else dest_language
    data['signType'] = 'v3'
    curtime = str(int(time.time()))
    data['curtime'] = curtime
    salt = str(uuid.uuid1())
    signStr = current_app.config['YOUDAO_APP_KEY'] + truncate(text) + salt + curtime + \
              current_app.config['YOUDAO_APP_SECRET']
    sign = encrypt(signStr)
    data['appKey'] = current_app.config['YOUDAO_APP_KEY']
    data['q'] = text
    data['salt'] = salt
    data['sign'] = sign
    response = do_request(data)

    if response.status_code != 200:
        return _('Error: the translation service failed.')

    translation = json.loads(response.text)["translation"][0]
    # translation = json.loads(response.text)
    # print(translation)
    return translation
