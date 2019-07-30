# -*- coding: utf-8 -*-
import json
import pprint
import uuid

import requests
import hashlib
import time

# YOUDAO_URL = 'http://openapi.youdao.com/api'
YOUDAO_URL = 'https://openapi.youdao.com/api'
APP_KEY = '0c5da03940d46b17'    # 应用 ID
APP_SECRET = 'bFsRiYrXoBK9sWI4nYTaMdf6fobMfhUv'  # 应用秘钥
"""
export YOUDAO_URL=https://openapi.youdao.com/api
export YOUDAO_APP_KEY=0c5da03940d46b17
export YOUDAO_APP_SECRET=bFsRiYrXoBK9sWI4nYTaMdf6fobMfhUv
"""


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
    return requests.post(YOUDAO_URL, data=data, headers=headers)


def connect():
    q = "今天天气不错，中午吃饭我们点了外卖。晚上我要回家吃鸭蛋。今天是周二啦！"
    data = {}
    data['from'] = 'zh-CHS'
    data['to'] = 'en'
    data['signType'] = 'v3'
    curtime = str(int(time.time()))
    data['curtime'] = curtime
    salt = str(uuid.uuid1())
    signStr = APP_KEY + truncate(q) + salt + curtime + APP_SECRET
    sign = encrypt(signStr)
    data['appKey'] = APP_KEY
    data['q'] = q
    data['salt'] = salt
    data['sign'] = sign
    # print(pprint.pformat(data))
    """
    {'appKey': '您的应用ID',
     'curtime': '1564455245',   # 当前的一个时间戳
     'from': 'EN',     # 源语言
     'q': 'test',      # 要翻译的文本
     'salt': '4b2cdb94-b275-11e9-9469-acde48001122',
     'sign': '2a6c94463f894ba8315895c00f9b766ef96e5236fac818647f5e7a5253d6d591',
     'signType': 'v3',
     'to': 'zh-CHS'}

    """
    # sys.exit(0)

    response = do_request(data)
    # print(response.content)
    # print(response.status_code)
    text = json.loads(response.text)
    # print(type(text))
    translation = text["translation"][0]
    return translation


if __name__ == '__main__':
    ret = connect()
    print(ret)
