#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Author:Lijiacai
Email:1050518702@qq.com
===========================================
CopyRight@JackLee.com
===========================================
"""

import os
import sys
import json
import time

import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.header import Header
from email.utils import parseaddr, formataddr


class Email(object):
    """
    注意：文件名需加上扩展名，查看邮箱时浏览器可解析显示
    >>> from LJC_tool.mail import Email
    >>> email_smtpserver = "smtp.exmail.qq.com"
    >>> email_port = "465"
    >>> email_sender = "xxx <xxxxx@xxxx.com>"
    >>> email_password = "xxxxxx"
    >>> email_receiver = ["xxxx <xxxxx@xxxx.com>>", "xxx <xxxxx@xxxx.com>>"]
    >>> email_subject = "测试"
    >>> email_ = Email(email_smtpserver, email_port, email_sender, email_password,
    >>>               email_receiver,
    >>>               email_subject)
    >>> result = "hello"
    >>> text = email_.appendText(result)
    >>> email_.attach(text)
    >>> file = email_.appendAttachment(email_.appendText(result), "测试.csv")
    >>> email_.attach(file)
    >>> email_.sendEmail()
    """

    # 初始化邮件相关配置
    def __init__(self, email_smtpserver, email_port, email_sender, email_password, email_receiver,
                 email_subject):
        self.__smtpserver = email_smtpserver
        self.__smtport = email_port
        self.__sender = email_sender
        self.__password = email_password
        self.__receiver = email_receiver
        self.__subject = email_subject + "    " + \
                         time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        self.__subject = Header(self.__subject, 'utf-8').encode()
        self.__msg = MIMEMultipart('mixed')
        self.__msg['Subject'] = self.__subject
        self.__msg['From'] = self._format_addr(self.__sender)
        self.__msg['To'] = ";".join(self.__receiver)

    def _format_addr(self, s):
        name, addr = parseaddr(s)
        self.send_addr = addr
        h = Header(name, "utf8")
        h.append(addr, "ascii")
        return h

    # 附加文本内容
    def appendText(self, text):
        text_plain = MIMEText(text, 'plain', 'utf-8')
        return text_plain

    # 附加图片 imgBytes:图片的二进制数据 imgName:图片名称
    def appendImage(self, imgBytes):
        image = MIMEImage(imgBytes)
        return image

    # 附加html htmlStr:字符串
    def appendHtml(self, html):
        text_html = MIMEText(html, 'html', 'utf-8')
        return text_html

    # 附加附件
    def appendAttachment(self, MIMEObject, attachName):
        MIMEObject.add_header('Content-Disposition',
                              'attachment', filename=attachName)
        return MIMEObject

    def attach(self, MIMEObject):
        self.__msg.attach(MIMEObject)

    # 发送邮件
    def sendEmail(self):
        smtp = None
        try:
            smtp = smtplib.SMTP_SSL(self.__smtpserver, self.__smtport)
            smtp.login(self.send_addr, self.__password)
            smtp.sendmail(self.__sender, self.__receiver,
                          self.__msg.as_string())

        except Exception as e:
            logging.exception(str(e))
        try:
            smtp.quit()
        except:
            pass
