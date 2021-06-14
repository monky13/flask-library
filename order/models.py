# 模型
from libs.db import db


class Order(db.Model):
    """
    管理员表
    """
    __tablename__ = 'order'

    id = db.Column(db.Integer, primary_key=True)  # id
    uid = db.Column(db.Integer, nullable=False)  # 占座学生id
    sid = db.Column(db.Integer, nullable=False)  # 座位id
    estimate_start_time = db.Column(db.DateTime)  # 预计开始时间
    estimate_end_time = db.Column(db.DateTime)  # 预计结束时间
    actual_start_time = db.Column(db.DateTime)  # 实际开始时间
    actual_end_time = db.Column(db.DateTime)  # 实际结束时间
    statu = db.Column(db.CHAR)  # 状态 1:当前，2：结束
