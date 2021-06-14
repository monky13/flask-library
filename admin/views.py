from math import ceil
from sqlite3 import InternalError
from flask import Blueprint
from flask import *
from collections import OrderedDict
from pymysql import IntegrityError
import numpy as np
import os
import cv2
import time

from comment.models import Comment
from libs.db import db
from libs.untils import gen_password
from notice.models import Notice
from notice.models import Warning
from user.loginc import save_avatar
from user.models import User
from forum.models import Forum
import datetime

admin_bp = Blueprint('admin', import_name='admin')
admin_bp.template_folder = './templates'
admin_bp.static_folder = './static'


# 视图函数
@admin_bp.route('/')
@admin_bp.route('/index')
def index():
    notice_list = Notice.query.order_by(Notice.id.desc())
    wid = 1
    warning = Warning.query.get(wid)
    return render_template('ahome.html', notice_list=notice_list, warning=warning)


# 学生管理
@admin_bp.route('/umng')
def user_mng():
    # 显示最新的前50条帖子
    # 获取帖子数据
    # 传入页码  根据页码  给出默认值
    page = int(request.args.get('page', 1))
    n_per_page = 10
    offset = (page - 1) * n_per_page
    # 当前页要显示的帖子
    # select * from forum order by updated desc limit 10 offset 20;
    user_list = User.query.order_by(User.id.desc()).limit(10).offset(offset)
    n_user = User.query.count()  # 帖子总数
    n_page = 5 if n_user >= 50 else ceil(n_user / n_per_page)  # 总页数
    print(n_page)
    return render_template('user_mng.html', page=page, n_page=n_page, user_list=user_list)


# 新增学生
@admin_bp.route('/adduser', methods=('GET', 'POST'))
def adduser():
    if request.method == 'POST':
        # 通过请求  将页面是接收的参数取出来  用户什么都没写
        # newline = ''   pandas  to_csv  dict字典
        # 装饰器封装方法  py基础中的  Java  String
        id = int(request.form.get('id', '').strip())
        name = request.form.get('name', '').strip()
        password = request.form.get('password', '').strip()
        gender = request.form.get('gender', '').strip()
        birthday = request.form.get('birthday', '').strip()
        institute = request.form.get('institute', '').strip()
        email = request.form.get('email', '').strip()
        bio = request.form.get('bio', '').strip()
        avatar = request.files.get('avatar')
        # 头像的处理  注册操作 添加数据
        # 创建一个user对象   相当于一条sql语句添加这么多的数据
        user = User(
            id=id,
            name=name,
            # 对数据库中存储的密码进行加密
            password=gen_password(password),
            # 性别 lamda 类似
            gender=gender if gender in ['male', 'female'] else 'male',
            birthday=birthday,
            institute=institute,
            email=email,
            bio=bio,
            credit=100,
            #     处理头像  绝对路径的正确规定
            avatar='/static/upload/%s' % id,
            # 显示当前时间
            create=datetime.datetime.now()
        )
        #    将对象添加到数据库中
        #     引入了数据库的事务的特征  事务回滚
        db.session.add(user)
        try:
            db.session.commit()
        except:
            db.session.rollback()
            # 如果出错了  打印一个提示信息
            return render_template('register.html', errors='该学号已存在,换一个')
        # 返回到管理页面
        save_avatar(id, avatar)
        return redirect('/admin/umng')
    else:
        return render_template('register.html')


# 重置密码
@admin_bp.route('/resetMm', methods=('GET', 'POST'))
def resetMm():
    uid = request.args.get("userId")
    user = User.query.filter(User.id == uid).first()
    user.password = gen_password("123456")
    db.session.commit()

    # 显示最新的前50条帖子
    # 获取帖子数据
    # 传入页码  根据页码  给出默认值
    page = int(request.args.get('page', 1))
    n_per_page = 10
    offset = (page - 1) * n_per_page
    # 当前页要显示的帖子
    # select * from forum order by updated desc limit 10 offset 20;
    user_list = User.query.order_by(User.id.desc()).limit(10).offset(offset)
    n_user = User.query.count()  # 帖子总数
    n_page = 5 if n_user >= 50 else ceil(n_user / n_per_page)  # 总页数
    print(n_page)
    # 提示：重置成功
    user_list = User.query.order_by(User.id.desc())
    return render_template('user_mng.html', page=page, n_page=n_page, user_list=user_list, errors='重置密码成功')


# 删除用户
@admin_bp.route('/delete', methods=('GET', 'POST'))
def delete():
    uid = request.args.get("userId")
    user = User.query.filter(User.id == uid).first()
    db.session.delete(user)
    db.session.commit()
    # 显示最新的前50条帖子
    # 获取帖子数据
    # 传入页码  根据页码  给出默认值
    page = int(request.args.get('page', 1))
    n_per_page = 10
    offset = (page - 1) * n_per_page
    # 当前页要显示的帖子
    # select * from forum order by updated desc limit 10 offset 20;
    user_list = User.query.order_by(User.id.desc()).limit(10).offset(offset)
    n_user = User.query.count()  # 帖子总数
    n_page = 5 if n_user >= 50 else ceil(n_user / n_per_page)  # 总页数
    print(n_page)
    # 提示：重置成功
    user_list = User.query.order_by(User.id.desc())
    return render_template('user_mng.html', page=page, n_page=n_page, user_list=user_list, errors='删除用户成功')


# 查找用户
@admin_bp.route('/ucheck', methods=('GET', 'POST'))
def ucheck():
    uid = request.form.get('userId')
    user_list = []
    user_list.append(User.query.get(uid))
    page = int(request.args.get('page', 1))
    n_page = 1
    return render_template('user_mng.html', page=page, n_page=n_page, user_list=user_list, errors='查找结果如下')


# 信用管理
@admin_bp.route('/cmng')
def credit_mng():
    # 显示最新的前50条帖子
    # 获取帖子数据
    # 传入页码  根据页码  给出默认值
    page = int(request.args.get('page', 1))
    n_per_page = 10
    offset = (page - 1) * n_per_page
    # 当前页要显示的帖子
    # select * from forum order by updated desc limit 10 offset 20;
    user_list = User.query.order_by(User.id.desc()).limit(10).offset(offset)
    n_user = User.query.count()  # 帖子总数
    n_page = 5 if n_user >= 50 else ceil(n_user / n_per_page)  # 总页数
    return render_template('credit_mng.html', page=page, n_page=n_page, user_list=user_list)


# 查找信用
@admin_bp.route('/check', methods=('GET', 'POST'))
def check():
    uid = request.form.get('userId')
    user_list = []
    user_list.append(User.query.get(uid))
    page = int(request.args.get('page', 1))
    n_page = 1
    return render_template('credit_mng.html', page=page, n_page=n_page, user_list=user_list, errors='查找结果如下')


# 重置信用
@admin_bp.route('/resetXy', methods=('GET', 'POST'))
def resetXy():
    uid = request.args.get("userId")
    user = User.query.filter(User.id == uid).first()
    if user.credit == 100:
        # 显示最新的前50条帖子
        # 获取帖子数据
        # 传入页码  根据页码  给出默认值
        page = int(request.args.get('page', 1))
        n_per_page = 10
        offset = (page - 1) * n_per_page
        # 当前页要显示的帖子
        # select * from forum order by updated desc limit 10 offset 20;
        user_list = User.query.order_by(User.id.desc()).limit(10).offset(offset)
        n_user = User.query.count()  # 帖子总数
        n_page = 5 if n_user >= 50 else ceil(n_user / n_per_page)  # 总页数
        return render_template('credit_mng.html', page=page, n_page=n_page, user_list=user_list, errors='该学生无需重置信用')
    else:
        user.credit = 100
        db.session.commit()
        # 显示最新的前50条帖子
        # 获取帖子数据
        # 传入页码  根据页码  给出默认值
        page = int(request.args.get('page', 1))
        n_per_page = 10
        offset = (page - 1) * n_per_page
        # 当前页要显示的帖子
        # select * from forum order by updated desc limit 10 offset 20;
        user_list = User.query.order_by(User.id.desc()).limit(10).offset(offset)
        n_user = User.query.count()  # 帖子总数
        n_page = 5 if n_user >= 50 else ceil(n_user / n_per_page)  # 总页数
        # 提示：重置成功
        return render_template('credit_mng.html', page=page, n_page=n_page, user_list=user_list, errors='重置信用成功')
    return redirect('/admin/cmng')


# 通知管理
@admin_bp.route('/nmng', methods=('GET', 'POST'))
def notice_mng():
    # 显示最新的前50条帖子
    # 获取帖子数据
    # 传入页码  根据页码  给出默认值
    page = int(request.args.get('page', 1))
    n_per_page = 10
    offset = (page - 1) * n_per_page
    # 当前页要显示的帖子
    # select * from forum order by updated desc limit 10 offset 20;
    notice_list = Notice.query.order_by(Notice.id.desc()).limit(10).offset(offset)
    n_notice = Notice.query.count()  # 帖子总数
    n_page = 5 if n_notice >= 50 else ceil(n_notice / n_per_page)  # 总页数
    return render_template('notice_mng.html', page=page, n_page=n_page, notice_list=notice_list)


# 通知添加
@admin_bp.route('/npost', methods=('GET', 'POST'))
def notice_post():
    if request.method == 'POST':
        title = request.form.get('title').strip()
        content = request.form.get('content').strip()
        # 标题不能为空
        if not title:
            return render_template('notice_post.html', error='标题不允许为空！')
        # 内容不能为空
        if not content:
            return render_template('notice_post.html', error='内容不允许为空！')
        else:
            notice = Notice(title=title, content=content)
            notice.created = datetime.datetime.now()
            db.session.add(notice)
            db.session.commit()
            # 提交之后返回到管理
            notice_list = Notice.query.order_by(Notice.id.desc())
            return redirect('/admin/nmng')
    else:
        return render_template('notice_post.html')


# 通知查看
@admin_bp.route('/nshow', methods=('GET', 'POST'))
def notice_show():
    nid = int(request.args.get('noticeId'))
    notice = Notice.query.get(nid)
    # 判断是否有帖子
    if notice is None:
        abort(404)
    else:
        return render_template('notice_show.html', notice=notice)


# 通知修改
@admin_bp.route('/modify', methods=('GET', 'POST'))
def modify():
    if request.method == 'POST':
        nid = int(request.form.get('noticeId'))
        content = request.form.get('content').strip()
        if not content:
            return render_template('notice_post.html', error='内容不允许为空！请重新发布通知')
        else:
            notice = Notice.query.get(nid)
            notice.content = content
            notice.updated = datetime.datetime.now()
            db.session.add(notice)
            db.session.commit()
            return redirect('/admin/nshow?noticeId=%s' % notice.id)
    else:
        nid = int(request.args.get('noticeId'))
        notice = Notice.query.get(nid)
        return render_template('notice_edit.html', notice=notice)


# 通知删除
@admin_bp.route('/ndelete', methods=('GET', 'POST'))
def notice_delete():
    nid = request.args.get("noticeId")
    notice = Notice.query.filter(Notice.id == nid).first()
    db.session.delete(notice)
    db.session.commit()
    return redirect('/admin/nmng')


# 更新警告
@admin_bp.route('/wudt', methods=('GET', 'POST'))
def warning_update():
    if request.method == 'POST':
        wid = int(request.form.get('warningId'))
        content = request.form.get('content').strip()
        if not content:
            return render_template('warning_update.html', error='内容不允许为空！请重新发布通知')
        else:
            warning = Warning.query.get(wid)
            warning.content = content
            db.session.add(warning)
            db.session.commit()
            return redirect('/admin/wudt')
    else:
        wid = 1
        warning = Warning.query.get(wid)
        return render_template('warning_update.html', warning=warning)


# view.py


# @admin_bp.route('/census', methods=('GET', 'POST'))
# def census():
#     k = User.query.order_by.desc(User.id).all()
#     local = {}
#     for i in k:
#         local[i.id] = i.institute
#
#     print(local)
#     return render_template('jl.html', local=local)


# 注：jsonify()将数据封装为json格式


# 违约统计
@admin_bp.route('/census', methods=('GET', 'POST'))
def census():
    return render_template('echarts.html',man=350,woman=150)


# # 性别统计
# @admin_bp.route('/g_census', methods=('GET', 'POST'))
# def gcensus():
#     print("hahahahhahahh")
#     women=10
#     men=20
#     return women,men
#
#
# # 学院统计
# @admin_bp.route('/icensus', methods=('GET', 'POST'))
# def icensus():
#     return render_template('i_census.html')


# 论坛管理
@admin_bp.route('/fmng', methods=('GET', 'POST'))
def forum_mng():
    # 显示最新的前50条帖子
    # 获取帖子数据
    # 传入页码  根据页码  给出默认值
    page = int(request.args.get('page', 1))
    n_per_page = 5
    offset = (page - 1) * n_per_page
    # 当前页要显示的帖子
    # select * from forum order by updated desc limit 10 offset 20;
    fr_list = Forum.query.order_by(Forum.updated.desc()).limit(5).offset(offset)
    n_forum = Forum.query.count()  # 帖子总数
    n_page = 5 if n_forum >= 50 else ceil(n_forum / n_per_page)  # 总页数

    # 获取帖子对应的作者
    uid_list = {fr.uid for fr in fr_list}  # 取出帖子对应的用户 ID
    # select id, nickname from user id in ...;
    # 取出之后是一个generator  里面是一个元组 转成字典
    users = dict(User.query.filter(User.id.in_(uid_list)).values('id', 'name'))
    return render_template('forum_mng.html', page=page, n_page=n_page, fr_list=fr_list, users=users)


# 查看帖子
@admin_bp.route('/fshow')
def show():
    fid = int(request.args.get('fid'))
    forum = Forum.query.get(fid)
    # 判断是否有帖子
    if forum is None:
        abort(404)
    else:
        user = User.query.get(forum.uid)
        # 获取当前帖子的所有评论
        # python 标准库中OrderedDict  有序字典  二维列表是可以转化为字典的  不能依赖字典的顺序
        # 字典和集合都是无序的
        comments = Comment.query.filter_by(fid=forum.id).order_by(Comment.created.desc())
        all_uid = {c.uid for c in comments}  # 所有评论的作者的ID
        cmt_users = dict(User.query.filter(User.id.in_(all_uid)).values('id', 'name'))
        comments = OrderedDict([[cmt.id, cmt] for cmt in comments])  # 将所有评论转成有序字典
        return render_template('forum_show.html', forum=forum, user=user, cmt_users=cmt_users, comments=comments)


# 删除帖子
@admin_bp.route('/fdelete')
def fdelete():
    fid = int(request.args.get('fid'))
    forum = Forum.query.get(fid)
    db.session.delete(forum)
    db.session.commit()
    return redirect('/admin/fmng')


# 退出登陆
@admin_bp.route('/logout')
def logout():
    session.pop('uid')
    return redirect('/')
