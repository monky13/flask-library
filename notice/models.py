# 模型
from datetime import datetime

from libs.db import db


class Notice(db.Model):
    """
    管理员表
    """
    __tablename__ = 'notice'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))  # 标题
    content = db.Column(db.Text)  # 内容
    created = db.Column(db.DateTime, default=datetime.now)  # 发布时间
    updated = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)  # 最后修改的时间


class Warning(db.Model):
    """
    管理员表
    """
    __tablename__ = 'warning'
    id = db.Column(db.Integer, primary_key=True)  # id
    content = db.Column(db.Text)  # 内容
