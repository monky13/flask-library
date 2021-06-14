import datetime
from math import ceil

from flask import Blueprint
from flask import *
from collections import OrderedDict

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import FlushError

from comment.models import Comment
from libs.db import db
from user.loginc import login_required
from user.models import User, Follow
from forum.models import Forum, Like

forum_bp = Blueprint('forum', import_name='forum')
forum_bp.template_folder = './templates'


@forum_bp.route('/')
@forum_bp.route('/index')
def index():
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
    return render_template('index.html', page=page, n_page=n_page, fr_list=fr_list,users=users)


# 发布帖子
# 利用装饰器检查用户是否登陆
@forum_bp.route('/post', methods=('POST', 'GET'))
@login_required
def post():
    if request.method == 'POST':
        content = request.form.get('content').strip()
        # 内容不能为空
        if not content:
            return render_template('post.html', error='帖子内容不允许为空！')
        else:
            forum = Forum(uid=session['uid'], content=content)
            forum.updated = datetime.datetime.now()
            db.session.add(forum)
            db.session.commit()
            # 提交之后返回到查看当前帖子页面
            return redirect('/forum/show?fid=%s' % forum.id)
    else:
        return render_template('post.html')


# 查看帖子
@forum_bp.route('/show')
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
        return render_template('show.html', forum=forum, user=user, cmt_users=cmt_users, comments=comments)


# 编辑帖子
# 后端的检查不要依赖于前端  该有的检查不能少
# 对于前端传来的所有数据对后端来说都不可信
# 所有的数据都必须检查
# 后端开发能自己获取的数据不要依赖前端的
# #参数和返回值能少则少，不要一次传递太多数据
@forum_bp.route('/edit', methods=('POST', 'GET'))
@login_required
def edit():
    if request.method == 'POST':
        fid = int(request.form.get('fid'))
        content = request.form.get('content').strip()
        if not content:
            return render_template('post.html', error='内容不允许为空！')
        else:
            forum = Forum.query.get(fid)
            # 取完微博id之后  做检查   我其他人能修改任何人的微博
            if forum.uid != session['uid']:
                abort(403)
            forum.content = content
            forum.updated = datetime.datetime.now()
            db.session.add(forum)
            db.session.commit()
            return redirect('/forum/show?fid=%s' % forum.id)
    else:
        fid = int(request.args.get('fid'))
        forum = Forum.query.get(fid)
        return render_template('edit.html', forum=forum)


# 删除
@forum_bp.route('/delete')
@login_required
def delete():
    fid = int(request.args.get('fid'))
    forum = Forum.query.get(fid)
    # 检查后端的id
    if forum.uid != session['uid']:
        abort(403)
    else:
        db.session.delete(forum)
        db.session.commit()
    return redirect('/forum')


@forum_bp.route('/like')
@login_required
def like():
    fid = int(request.args.get('fid'))
    forum = Forum.query.get(fid)
    # 检查后端的id
    if session['uid'] == None:
        abort(403)
    else:
        forum.n_like = forum.n_like + 1
        db.session.commit()
    return redirect('/forum')