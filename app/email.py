# -*- coding: utf-8 -*-
from threading import Thread
from flask import current_app
from flask_mail import Message
from app import mail


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


# def send_email(subject, sender, recipients, text_body, html_body):
#     msg = Message(subject, sender=sender, recipients=recipients)
#     msg.body = text_body
#     msg.html = html_body
#     Thread(target=send_async_email,
#            args=(current_app._get_current_object(), msg)).start()


def send_email(subject, sender, recipients, text_body, html_body,
               attachments=None, sync=False):
    """
    发送电子邮件封装方法
    :param subject:
    :param sender:
    :param recipients:
    :param text_body:
    :param html_body:
    :param attachments:
    :param sync:
    :return:
    """
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    # 添加对于文件附件的支持
    # attach 方法接收三个定义的附件的参数: 文件名 媒体类型以及实际的文件数据
    # 文件名就是收件人看到的 实际与附件相关的名称
    # 媒体类型定义附件类型
    # 实际文件数据包含附件内容的字符串或字节序列
    if attachments:
        # send_email()的attachments参数将成为一个元组列表，每个元组将有三个元素对应于attach()的三个参数。
        # 因此，我需要将此列表中的每个元素作为参数发送给attach()
        for attachment in attachments:
            msg.attach(*attachment)
    if sync:
        # 同步发送
        mail.send(msg)
    else:
        # 异步发送
        Thread(target=send_async_email,
            args=(current_app._get_current_object(), msg)).start()
