from math import ceil
from sqlite3 import InternalError

from flask import Blueprint
from flask import *
from pymysql import IntegrityError
import numpy as np
import os
import cv2
import time
from libs.db import db
from libs.untils import gen_password, check_password
from admin.models import Admin
from user.loginc import save_avatar
from user.models import User
from feedback.models import Feedback
import datetime

admin_bp = Blueprint('admin', import_name='admin')
admin_bp.template_folder = './templates'
admin_bp.static_folder = './static'


# 视图函数
# 注册  头像的上传  给出不同的请求方式 判断请求方式
@admin_bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        # 通过请求  将页面是接收的参数取出来  用户什么都没写
        # newline = ''   pandas  to_csv  dict字典
        # 装饰器封装方法  py基础中的  Java  String
        id = int(request.form.get('id', '').strip())
        name = request.form.get('name', '').strip()
        password = request.form.get('password', '').strip()
        gender = request.form.get('gender', '').strip()
        bio = request.form.get('bio', '').strip()
        institute = request.form.get('institute', '').strip()
        birthday = request.form.get('birthday', '').strip()
        email = request.form.get('email', '').strip()
        avatar = request.files.get('avatar')
        print(id)
        # 头像的处理  注册操作 添加数据
        # 创建一个user对象   相当于一条sql语句添加这么多的数据
        user = User(
            id=id,
            name=name,
            # 对数据库中存储的密码进行加密
            password=gen_password(password),
            #     性别   lamda 类似
            gender=gender if gender in ['male', 'female'] else 'male',
            bio=bio,
            institute=institute,
            birthday=birthday,
            #     处理头像  绝对路径的正确规定
            avatar='/static/upload/%s' % id,
            # 显示当前时间
            create=datetime.datetime.now(),
            email=email
        )

        #    将对象添加到数据库中

        #     引入了数据库的事务的特征  事务回滚
        """
           1.明确处理每一个异常
           2.try和except之间的语句、代码 越少越好  
           3.不要隐藏异常，而应该进行定向的处理
           """
        db.session.add(user)
        db.session.commit()
        try:
            db.session.commit()
        except:
            db.session.rollback()
            # 如果出错了  打印一个提示信息
            return render_template('register.html', errors='该学号已存在,换一个')

        # 返回到登陆页面
        save_avatar(id, avatar)
        return redirect('/admin/index')
    else:
        return render_template('register.html')

    #     异常的处理  当添加的对象  没有按照数据表的规定进行添加的话  会报错  抓异常
    #    异常：抓取（抓取异常 ）  抛出（一种不负责  没有用处  bug进行处理）  各有千秋

# 登陆


@admin_bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        id = request.form.get('id', '').strip()
        password = request.form.get('password', '').strip()

        # 利用sqlalchemy的查询方式
        admin = Admin.query.filter_by(id=id).first()
        # 判断是否可以拿到
        if admin is None:
            return render_template('login.html', error='账号有误，请重新输入')
        # 判断密码是否正确
        if check_password(password, admin.password):
            # 如果密码正确，记录用户登录状态   退出登录  session记录用户的登陆情况
            session['uid'] = admin.id
            # 根据用户的状态去显示用户信息
            return redirect('/admin/index')
        else:
            return render_template('login.html', error='密码不正确')

    else:
        if 'uid' in session:
            return redirect('//admin/index')
        else:
            return render_template('login.html')


# 退出登陆
@admin_bp.route('/logout')
def logout():
    session.pop('uid')
    return redirect('/')


# 退出登陆
@admin_bp.route('/index')
def index():
    return redirect('/admin/register')
