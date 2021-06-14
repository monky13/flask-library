# 分层清晰会让别人更容易的看你的代码
# 也会更容易的区分python web的交互方式
# 如果创建在一个大的包中  会造成app循环使用
# 第一行使用是user，报错  user找不到
# flask通病  全部都是由自己导入

from flask import Flask

from comment.views import comment_bp
from libs.db import db
from order import order_bp
from user.views import user_bp, redirect
from admin import admin_bp
from forum.views import forum_bp
from test.views import test_bp

app = Flask(__name__)
app.secret_key = 'M\\xD6\\xD0\\xB9\\xFA\\xB1\\xEA'

# 注册蓝图  alt+enter
app.register_blueprint(order_bp, url_prefix='/order')
app.register_blueprint(user_bp, url_prefix='/user')
app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(forum_bp, url_prefix='/forum')
app.register_blueprint(comment_bp, url_prefix='/comment')
app.register_blueprint(test_bp, url_prefix='/test')


# 数据库的链接
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:123456@localhost:3306/library_order'
app.config['SQLALCHENY_TRACK_MODIFICATION'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True  # 禁止数据的修改追踪(需要消耗资源)
db.init_app(app)


@app.route('/')
def home():
    return redirect('/user/')


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000, debug=True)
