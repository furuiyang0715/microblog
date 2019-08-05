# -*- coding: utf-8 -*-
import imghdr

from flask import current_app
from qiniu import Auth, put_data


def upload_image(file_data):
    """
    上传图片到七牛
    :param file_data: bytes 文件
    :return: file_name
    """
    access_key = current_app.config['QINIU_ACCESS_KEY']
    secret_key = current_app.config['QINIU_SECRET_KEY']
    # 构建鉴权对象
    q = Auth(access_key, secret_key)
    # 要上传的空间
    bucket_name = current_app.config['QINIU_BUCKET_NAME']
    # 上传到七牛后保存的文件名 应该跟相应的用户有关
    # key = 'my-python-七牛.png'
    key = None
    # 生成上传 Token，可以指定过期时间等
    token = q.upload_token(bucket_name, expires=1800)
    # # 要上传文件的本地路径
    # localfile = '/Users/jemy/Documents/qiniu.png'
    # ret, info = put_file(token, key, localfile)
    ret, info = put_data(token, key, file_data)
    return ret['key']


def image_file(value):
    """
    检查是否是图片文件
    :param value:
    :return:
    """
    try:
        file_type = imghdr.what(value)   # eg. 'png'
    except Exception:
        raise ValueError('Invalid image.')
    else:
        if not file_type:
            raise ValueError('Invalid image.')
        else:
            return value
