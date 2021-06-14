# 模型
from libs.db import db


class Seat(db.Model):
    """
    管理员表
    """
    __tablename__ = 'seat'

    id = db.Column(db.Integer, primary_key=True)  # id
    floor = db.Column(db.String(128), nullable=True)  # 楼层
    row = db.Column(db.Integer, nullable=False)  # 排
    col = db.Column(db.Integer, nullable=False)  # 列
    uid = db.Column(db.Integer, nullable=False)  # 占座学生id
