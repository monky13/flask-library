# 模型
from libs.db import db


class Credit(db.Model):
    """
    管理员表
    """
    __tablename__ = 'credit'

    id = db.Column(db.Integer, primary_key=True)  # id
    uid = db.Column(db.Integer, nullable=False)  # 学生id]
    sid = db.Column(db.Integer, nullable=True)  # 座位id
    type = db.Column(db.String(20), nullable=False)  # 类型
    time = db.Column(db.DateTime)  # 时间
