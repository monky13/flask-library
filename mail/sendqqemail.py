#!/usr/bin/python
# -*- coding: UTF-8 -*-

import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr


class QQMail:
    def __init__(self, smtp_email_account, smtp_author_code):
        self.smtp_email_account = smtp_email_account
        self.smtp_author_code = smtp_author_code
        self.smtp_server = smtplib.SMTP_SSL(
            "smtp.qq.com", 465)  # 发件人邮箱中的SMTP服务器，端口是25
        # 括号中对应的是发件人邮箱账号、邮箱密码
        self.smtp_server.login(smtp_email_account, smtp_author_code)

    def send_email(self, recv_eamil: str, send_str: str):
        ret = True
        try:
            msg = MIMEText(send_str, 'plain', 'utf-8')
            # 括号里的对应发件人邮箱昵称、发件人邮箱账号
            msg['From'] = formataddr(
                ["图书馆预约", self.smtp_email_account])
            # 括号里的对应收件人邮箱昵称、收件人邮箱账号
            msg['To'] = formataddr(["FK", recv_eamil])
            msg['Subject'] = "图书馆预约通知"                # 邮件的主题，也可以说是标题

            self.smtp_server.sendmail(self.smtp_email_account, [
                                      recv_eamil, ], msg.as_string())  # 括号中对应的是发件人邮箱账号、收件人邮箱账号、发送邮件
        except Exception as e:  # 如果 try 中的语句没有执行，则会执行下面的 ret=False
            print(str(e))
            ret = False
        return ret
