from datetime import datetime

from libs.db import db


class Comment(db.Model):
    '''评论表'''
    __tablename__ = 'comment'

    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.Integer, nullable=False)  # 评论的ID
    fid = db.Column(db.Integer, nullable=False)  # 被评论的帖子的ID
    cid = db.Column(db.Integer, nullable=False, default=0)  # 回复的评论的ID
    rid = db.Column(db.Integer, nullable=False, default=0)  # 回复的回复的ID
    content = db.Column(db.Text)  # 内容
    created = db.Column(db.DateTime, default=datetime.now)  # 评论时间
