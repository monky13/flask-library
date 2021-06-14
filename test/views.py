from flask import *

test_bp = Blueprint('test', import_name='test')
test_bp.template_folder = './templates'


# 发布
# 利用装饰器检查用户是否登陆
@test_bp.route('/')
@test_bp.route('/post', methods=('POST', 'GET'))
def post():
    return render_template('4用户管理.html')
