import datetime
from math import ceil
from threading import Condition

from flask import Blueprint
from flask import *
from collections import OrderedDict

from sqlalchemy import func, exists
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import FlushError

from libs.db import db
from seat.models import Seat
from user.loginc import login_required
from user.models import User
from order.models import Order
from mail.sendqqemail import QQMail
from credit.models import Credit

order_bp = Blueprint('order', import_name='order')
order_bp.template_folder = './templates'


# 发布
# 利用装饰器检查用户是否登陆
# 负责mail分送

# my_sender = '2439579750@qq.com'
# my_pass = 'bbbbbbp33'
#
#
# class MailModule:
#     def __init__(self):
#         self.login(my_sender, my_pass)
#
#     def login(self, sender_eamil, author_code):
#         self.qq_mail_engine = QQMail(sender_eamil, author_code)
#
#     def send_email(self, recv_eamil: str, send_str: str):
#         self.qq_mail_engine.send_email(
#             recv_eamil, send_str)
#
#
# mail_module = MailModule()


# 预约记录
@order_bp.route('/orecord', methods=('POST', 'GET'))
@login_required
def order_record():
    # 传入页码  根据页码  给出默认值
    uid = session.get('uid')

    page = int(request.args.get('page', 1))
    n_per_page = 10
    offset = (page - 1) * n_per_page
    # 当前页显示
    order_list = Order.query.filter_by(uid=uid).order_by(Order.estimate_start_time.desc()).limit(10).offset(offset)
    n_order = Order.query.count()  # 总数
    n_page = 5 if n_order >= 50 else ceil(n_order / n_per_page)  # 总页数

    seat_list = []
    sid_list = {order.sid for order in order_list}
    for sid in sid_list:
        seat_list.append(Seat.query.get(sid))

    print(seat_list)

    return render_template('order_record.html', page=page, n_page=n_page, order_list=order_list, seat_list=seat_list)


# 信用记录
@order_bp.route('/crecord', methods=('POST', 'GET'))
@login_required
def credit_record():
    # 传入页码  根据页码  给出默认值
    uid = session.get('uid')
    user = User.query.get(uid)

    page = int(request.args.get('page', 1))
    n_per_page = 10
    offset = (page - 1) * n_per_page
    # 当前页显示
    credit_list = Credit.query.filter_by(uid=user.id).order_by(Credit.time.desc()).limit(10).offset(offset)
    n_credit = Credit.query.count()  # 总数
    n_page = 5 if n_credit >= 50 else ceil(n_credit / n_per_page)  # 总页数

    return render_template('credit_record.html', page=page, n_page=n_page, credit_list=credit_list, user=user)


#
# @order_bp.route('/sea')
# def sea():
#     '''列表'''
#     #uid = session.get('uid')
#     seat_list = Seat.query.order_by(Seat.id.desc())
#     return render_template('sea.html', seat_list=seat_list)

# 座位表
@order_bp.route('/seats', methods=('POST', 'GET'))
def seats():
    floor = int(request.args.get('floorId', 1))
    col_max = 4
    row_max = 2
    uid = session.get('uid')
    user = User.query.filter(User.id == uid).first()
    ret = db.session.query(exists().where(Seat.uid == uid)).scalar()
    print(ret)
    if ret:
        seat = Seat.query.filter(Seat.uid == uid).one()
    else:
        seat = False
    print(seat)

    seat_list = Seat.query.filter_by(floor=floor)
    sid_list = [seat.id for seat in seat_list]

    i = 0
    seatList = []
    for row in range(2):
        seatList.append([])
        for column in range(4):
            seatList[row].append(Seat.query.get(sid_list[i]))
            i = i + 1
    print(seatList)

    return render_template('seats.html', seatList=seatList, user=user, seat=seat, col_max=col_max, row_max=row_max,
                           floor=floor)


# 实现预约
@order_bp.route('/book')
@login_required
def book():
    sid = request.args.get("seatId")
    time = int(request.args.get("time"))
    print(sid, time)
    uid = session.get('uid')
    # 先根据用户id查找是否已经预约
    # 如果已经预约那么就无法继续预约
    ifOder = Seat.query.filter_by(uid=uid).first()
    if ifOder != None:
        # return redirect(url_for('/order/seats', errors='您当前存在预约'))
        return redirect('/order/seats')

    print("成功")
    order = Order(
        uid=uid,
        sid=sid,
        estimate_start_time=datetime.datetime.now(),
        estimate_end_time=datetime.datetime.now() + datetime.timedelta(minutes=time),
        statu=1
    )
    print(order.id)
    db.session.add(order)
    db.session.commit()

    Seat.query.filter_by(id=sid).update({'uid': uid})
    db.session.commit()
    # user = User.query.filter_by(id=uid).first()
    # # mail_module.send_email(user.email, "您已经预约" +
    # #                        str(datetime.datetime.now())+"时间,座位号为:"+sid)
    # seat_list = Seat.query.order_by(Seat.id.desc())
    return redirect('/order/seats')


# 签到
@order_bp.route('/signin', methods=('POST', 'GET'))
@login_required
def signin():
    uid = session.get('uid')
    sid = request.args.get("seatId")

    order = Order.query.filter_by(sid=sid, uid=uid, statu=1).first()
    order.actual_start_time = datetime.datetime.now()
    db.session.commit()
    return redirect("/order/seats")


# 签退
@order_bp.route('/signout', methods=('POST', 'GET'))
@login_required
def signout():
    uid = session.get('uid')
    sid = request.args.get("seatId")

    order = Order.query.filter_by(sid=sid, uid=uid, statu=1).first()
    order.actual_end_time = datetime.datetime.now()
    order.statu = 2
    db.session.commit()
    Seat.query.filter_by(id=sid).update({'uid': '0'})
    db.session.commit()
    return redirect("/order/seats")
