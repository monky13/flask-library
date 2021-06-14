# 模型
from datetime import datetime
from libs.db import db


class User(db.Model):
    """用户表"""
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)  # 学号
    name = db.Column(db.String(20), nullable=False)  # 姓名
    password = db.Column(db.String(128), default='123')  # 密码
    gender = db.Column(db.String(10), default='unkonw')  # 性别
    birthday = db.Column(db.Date, default='1990-01-01')  # 生日
    institute = db.Column(db.String(20), default='商学院')  # 学院
    email = db.Column(db.String(64),nullable=True)  # 邮箱
    bio = db.Column(db.String(255),nullable=True)  # 简介
    avatar = db.Column(db.String(128),nullable=True)  # 头像
    credit = db.Column(db.Integer,default=100)  # 信用
    create = db.Column(db.DateTime, default=datetime.now)  # 创建时间


class Follow(db.Model):
    '''关注表'''
    __tablename__ = 'follow'
    uid = db.Column(db.Integer, primary_key=True)
    fid = db.Column(db.Integer, primary_key=True)