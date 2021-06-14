from datetime import datetime

from libs.db import db


class Forum(db.Model):
    __tablename__ = 'forum'
    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.Integer, nullable=False)  # 用户id
    content = db.Column(db.Text)  # 内容
    created = db.Column(db.DateTime, default=datetime.now)  # 发布时间
    updated = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)  # 最后修改的时间
    n_like = db.Column(db.Integer, default=0)  # 当前的点赞数量


class Like(db.Model):
    __tablename__ = 'like'
    uid = db.Column(db.Integer, primary_key=True)
    wid = db.Column(db.Integer, primary_key=True)
