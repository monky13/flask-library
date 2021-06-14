from flask import Blueprint
from flask import abort
from flask import request
from flask import redirect
from flask import session

from comment.models import Comment
from libs.db import db
from user.loginc import login_required

comment_bp = Blueprint('comment', import_name='comment')

# 发表评论  全部是跳转  因为是在某一条微博下
# 加登陆验证 登陆状态下
@comment_bp.route('/post', methods=('POST',))
@login_required
def post():
    uid = session['uid']
    fid = int(request.form.get('fid'))
    content = request.form.get('content')
    cmt = Comment(uid=uid, fid=fid, content=content)
    db.session.add(cmt)
    db.session.commit()
    return redirect('/forum/show?fid=%s' % fid)


# 发表回复
@comment_bp.route('/reply', methods=('POST',))
@login_required
def reply():
    uid = session['uid']
    fid = int(request.form.get('fid'))
    cid = int(request.form.get('cid'))  # 主评论的id  加上
    rid = int(request.form.get('rid'))  # 回复的id
    content = request.form.get('content')
    cmt = Comment(uid=uid, fid=fid, cid=cid, rid=rid, content=content)
    db.session.add(cmt)
    db.session.commit()
    return redirect('/forum/show?fid=%s' % fid)