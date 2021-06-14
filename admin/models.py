# 模型
from libs.db import db


class Admin(db.Model):
    """
    管理员表
    """
    __tablename__ = 'admin'

    id = db.Column(db.Integer, primary_key=True)  # id
    password = db.Column(db.String(128), nullable=True)  # 密码
