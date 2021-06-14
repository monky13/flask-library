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
from notice.models import Notice, Warning
from user.loginc import save_avatar
from user.models import User
from admin.models import Admin
import datetime

user_bp = Blueprint('user', import_name='user')
user_bp.template_folder = './templates'
user_bp.static_folder = './static'


# 视图函数
@user_bp.route('/')
@user_bp.route('/home', methods=('POST', 'GET'))
def index():
    notice_list = Notice.query.order_by(Notice.id.desc())
    wid = 1
    warning = Warning.query.get(wid)
    return render_template('uhome.html', notice_list=notice_list, warning=warning)


# 登陆
@user_bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        usertype = int(request.form.get('usertype', '').strip())
        id = int(request.form.get('id', '').strip())
        password = request.form.get('password', '').strip()
        # 管理员登录
        if usertype == 2:
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
            # 利用sqlalchemy的查询方式
            user = User.query.filter_by(id=id).first()
            # 判断是否可以拿到
            if user is None:
                return render_template('login.html', error='账号有误，请重新输入')
            # 判断密码是否正确
            if check_password(password, user.password):
                # 如果密码正确，记录用户登录状态   退出登录  session记录用户的登陆情况
                session['uid'] = user.id
                # 根据用户的状态去显示用户信息
                return redirect('/user/home')
            else:
                return render_template('login.html', error='密码不正确')
    else:
        if 'uid' in session:
            return redirect('/user/home')
        else:
            return render_template('login.html')


# 退出登陆
@user_bp.route('/logout')
def logout():
    session.pop('uid')
    return redirect('/')


# 更新
@user_bp.route('/update', methods=('GET', 'POST'))
def to_update():
    if request.method == 'POST':
        id = request.form.get('id', '').strip()
        name = request.form.get('name', '').strip()
        password = request.form.get('password', '').strip()
        gender = request.form.get('gender', '').strip()
        birthday = request.form.get('birthday', '').strip()
        institute = request.form.get('institute', '').strip()
        email = request.form.get('email', '').strip()
        bio = request.form.get('bio', '').strip()
        # 注册操作 添加数据
        # 创建一个user对象   相当于一条sql语句添加这么多的数据
        user = User(
            id=id,
            name=name,
            # 对数据库中存储的密码进行加密
            password=gen_password(password),
            # 性别   lamda 类似
            gender=gender if gender in ['male', 'female'] else 'male',
            birthday=birthday,
            institute=institute,
            email=email,
            bio=bio,
            # 显示当前时间
            create=datetime.datetime.now()
        )
        # User.query(user.name ==name).update()
        user = User.query.filter(user.name == name).first()
        user.password = gen_password(password)
        user.gender = gender
        user.birthday = birthday
        user.institute = institute
        user.email = email
        user.bio = bio
        db.session.commit()
        try:
            db.session.commit()
        except:
            db.session.rollback()
        return redirect('/user/info')
    else:
        uid = session.get('uid')
        if uid:
            user = User.query.get(uid)
        return render_template('update.html', user=user)


@user_bp.route("/changeImg1", methods=('GET', 'POST'))
def tochangeImg():
    user = User()
    user.id = int(request.args.get('uid'))
    return render_template('changeImg.html', user=user)


@user_bp.route("/changeImg", methods=('GET', 'POST'))
def changeImg():
    if request.method == 'POST':
        id = request.form.get('id', '').strip()
        avatar = request.files.get('avatar')
        # 头像的处理  注册操作 添加数据
        # 创建一个user对象   相当于一条sql语句添加这么多的数据
        user = User(
            id=id,
            avatar='/static/upload/%s' % id,
        )
        user.avatar = avatar
        save_avatar(id, avatar)
        try:
            db.session.commit()
        except:
            db.session.rollback()
        return redirect('/user/info')
    else:
        return redirect('/user/info')


# 个人信息
@user_bp.route('/info')
def info():
    '''用户个人资料页'''
    uid = session.get('uid')
    user = User.query.get(uid)
    return render_template('info.html', user=user)


# 采集人脸
@user_bp.route('/take_face', methods=('GET', 'POST'))
def take_face():
    cap = cv2.VideoCapture(0)  # 打开摄像头
    face_detector = cv2.CascadeClassifier(
        'user/haarcascade_frontalface_alt.xml')  # 识别人脸
    print(face_detector, "==============")
    isFace = False  # 告诉我们是否检测出了人脸
    while True:
        flag, frame = cap.read()
        gray = cv2.cvtColor(frame, code=cv2.COLOR_BGR2GRAY)
        face_zones = face_detector.detectMultiScale(gray,
                                                    scaleFactor=1.2,
                                                    minNeighbors=5,
                                                    minSize=(80, 80),
                                                    maxSize=(320, 320))
        for x, y, w, h in face_zones:
            isFace = True
            face = frame[y + 1:y + h, x + 1:x + w]  # 彩色人脸
            cv2.rectangle(frame, pt1=(x, y), pt2=(x + w, y + h),
                          color=[0, 0, 255], thickness=1)
        if isFace:
            cv2.imshow('face', face)  # 有人脸，显示人脸
        else:
            cv2.imshow('face', frame)  # 没有人脸，显示画面
        key = cv2.waitKey(1000 // 24)
        isFace = False
        if key == ord('q'):
            break
        elif key == ord('w'):  # 说明采集的人脸，自己比较满意， 保存一下
            os.makedirs('user/face_certification', exist_ok=True)
            filename = os.listdir('user/face_certification')
            num = len(filename)
            face = cv2.cvtColor(face, code=cv2.COLOR_BGR2GRAY)  # 灰度化处理
            face = cv2.resize(face, dsize=(128, 128))  # 尺寸调整
            face = cv2.equalizeHist(face)  # 均衡化
            cv2.imwrite('user/face_certification/%d.jpg' % (num), face)  # 保存图片
            user = User.query.get(session['uid'])
            print(user.id, "---", session['uid'])
            user.num = num
            db.session.commit()
            break
    cv2.destroyAllWindows()
    cap.release()

    if 'uid' in session:
        return redirect('/user/info')
    else:
        print("采集失败")


# 人脸签到
@user_bp.route('/face_in', methods=("GET", "POST"))
def face_in():
    cap = cv2.VideoCapture(0)
    face_detector = cv2.CascadeClassifier(
        'user/haarcascade_frontalface_alt.xml')
    face_recognizer = cv2.face.LBPHFaceRecognizer_create(threshold=200)  # 训练
    faces = os.listdir('user/face_certification')  # 列表
    print(faces)
    if len(faces) == 0:
        return render_template('login.html', error="没有采集头像，登录失败")
    X = np.asarray(
        [cv2.imread('user/face_certification/' + face)[:, :, 0] for face in faces])
    y = np.asarray([int(face.split('.')[0]) for face in faces])
    face_recognizer.train(X, y)  # train，算法，知道哪个人脸可以登录
    count = 0
    isExit = False
    while True:
        flag, frame = cap.read()
        if flag == False:
            break
        gray = cv2.cvtColor(frame, code=cv2.COLOR_BGR2GRAY)
        face_zones = face_detector.detectMultiScale(gray, scaleFactor=1.2,
                                                    minNeighbors=5,
                                                    minSize=(80, 80),
                                                    maxSize=(320, 320))
        for x, y, w, h in face_zones:
            face = gray[y:y + h, x:x + w]
            face = cv2.resize(face, (128, 128))
            # 均衡化
            face = cv2.equalizeHist(face)
            # 预测，返回标签和置信度
            label, confidence = face_recognizer.predict(face)
            print('--------------', label, confidence)
            cv2.rectangle(frame, pt1=(x, y), pt2=(x + w, y + h),
                          color=[0, 0, 255], thickness=2)
            user = User.query.filter_by(num=label).first()
            if (user == None):
                break
            if label == -1.:  # 等于-1没有找到这个人
                print('----------------刷脸登陆登陆失败---------------------')
                time.sleep(2)
                count += 1
            elif label == user.num:  # 验证成功
                # print('+++++++++++++++++++++刷脸登陆++++++++++++++++++++++++')
                # v = cv2.VideoCapture('user/config/ttnk.mp4')
                # while True:
                #     flag, frame = v.read()
                #     if flag == False:
                #         isExit = True
                #         break
                #     cv2.imshow('face', frame)
                #     cv2.waitKey(1000 // 24)
                isExit = True
                break
            else:
                return render_template('login.html', error="登录失败")
        if count >= 3:
            break
        if isExit:
            break
        cv2.imshow('登录中...', frame)
        key = cv2.waitKey(1000 // 24)
        if key == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()
    if (isExit == True):
        session['uid'] = user.id
        # 根据用户的状态去显示用户信息
        return redirect('/user/info')
    else:
        return render_template('login.html', error="登录失败")


# 人脸签退
@user_bp.route('/face_out', methods=("GET", "POST"))
def face_out():
    cap = cv2.VideoCapture(0)
    face_detector = cv2.CascadeClassifier(
        'user/haarcascade_frontalface_alt.xml')
    face_recognizer = cv2.face.LBPHFaceRecognizer_create(threshold=200)  # 训练
    faces = os.listdir('user/face_certification')  # 列表
    print(faces)
    if len(faces) == 0:
        return render_template('login.html', error="没有采集头像，登录失败")
    X = np.asarray(
        [cv2.imread('user/face_certification/' + face)[:, :, 0] for face in faces])
    y = np.asarray([int(face.split('.')[0]) for face in faces])
    face_recognizer.train(X, y)  # train，算法，知道哪个人脸可以登录
    count = 0
    isExit = False
    while True:
        flag, frame = cap.read()
        if flag == False:
            break
        gray = cv2.cvtColor(frame, code=cv2.COLOR_BGR2GRAY)
        face_zones = face_detector.detectMultiScale(gray, scaleFactor=1.2,
                                                    minNeighbors=5,
                                                    minSize=(80, 80),
                                                    maxSize=(320, 320))
        for x, y, w, h in face_zones:
            face = gray[y:y + h, x:x + w]
            face = cv2.resize(face, (128, 128))
            # 均衡化
            face = cv2.equalizeHist(face)
            # 预测，返回标签和置信度
            label, confidence = face_recognizer.predict(face)
            print('--------------', label, confidence)
            cv2.rectangle(frame, pt1=(x, y), pt2=(x + w, y + h),
                          color=[0, 0, 255], thickness=2)
            user = User.query.filter_by(num=label).first()
            if (user == None):
                break
            if label == -1.:  # 等于-1没有找到这个人
                print('----------------刷脸登陆登陆失败---------------------')
                time.sleep(2)
                count += 1

            elif label == user.num:  # 验证成功
                # print('+++++++++++++++++++++刷脸登陆++++++++++++++++++++++++')
                # v = cv2.VideoCapture('user/config/ttnk.mp4')
                # while True:
                #     flag, frame = v.read()
                #     if flag == False:
                #         isExit = True
                #         break
                #     cv2.imshow('face', frame)
                #     cv2.waitKey(1000 // 24)
                isExit = True
                break
            else:
                return render_template('login.html', error="登录失败")
        if count >= 3:
            break
        if isExit:
            break
        cv2.imshow('登录中...', frame)
        key = cv2.waitKey(1000 // 24)
        if key == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()
    if (isExit == True):
        session['uid'] = user.id
        # 根据用户的状态去显示用户信息
        return redirect('/user/info')
    else:
        return render_template('login.html', error="登录失败")
