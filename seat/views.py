import datetime
from math import ceil

from flask import Blueprint
from flask import *
from collections import OrderedDict

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import FlushError

from libs.db import db
from user.loginc import login_required
from user.models import User
from seat.models import Seat

seat_bp = Blueprint('seat', import_name='seat')
seat_bp.template_folder = './templates'

# 列表
