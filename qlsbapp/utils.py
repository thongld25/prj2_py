import json, os

from sqlalchemy import func

from qlsbapp import app, db
from qlsbapp.models import Sanbong, User, Receipt, UserRole
import hashlib


def read_json(path):
    with open(path, "r") as f:
        return json.load(f)

def load_sanbong(sanbong_id):
    sanbong = Sanbong.query.filter(Sanbong.id.__eq__(sanbong_id)).first()
    return sanbong


def load_sanbongs(kw=None, from_price=None, to_price=None, page=1):
    sanbongs = Sanbong.query.filter(Sanbong.active.__eq__(True))

    if kw:
        sanbongs = sanbongs.filter(Sanbong.name.contains(kw))

    if from_price:
        sanbongs = sanbongs.filter(Sanbong.price.__ge__(float(from_price)))

    if to_price:
        sanbongs = sanbongs.filter(Sanbong.price.__le__(float(to_price)))

    page_size = app.config['PAGE_SIZE']
    start = (page - 1) * page_size
    end = start + page_size
    return sanbongs.slice(start, end).all()
    # return read_json(os.path.join(app.root_path, 'data/sanbong.json'))

def load_receipt(user_id):
    receipts = Receipt.query.filter(Receipt.user_id.__eq__(user_id)).all()
    return receipts

def get_sanbong_by_id(sanbong_id):
    return Sanbong.query.get(sanbong_id)


def add_user(name, username, password, **kwargs):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    user = User(name=name.strip(),
                username=username.strip(),
                password=password,
                email=kwargs.get('email'),
                phone=kwargs.get('phone'),
                avatar=kwargs.get('avatar'))

    db.session.add(user)
    db.session.commit()

def add_receipt(user_id, sanbong_id, time_play, time_frame, status):
    receipt = Receipt(user_id=user_id,
                      sanbong_id=sanbong_id,
                      time_play=time_play,
                      time_frame=time_frame,
                      status = status)

    db.session.add(receipt)
    db.session.commit()




def check_login(username, password, role):
    if username and password:
        password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())

        return User.query.filter(User.username.__eq__(username.strip()),
                                 User.password.__eq__(password),
                                 User.user_role.__eq__(role)).first()

def get_user_by_id(user_id):
    return User.query.get(user_id)

def get_sanbong_by_id(sb_id):
    return Sanbong.query.get(sb_id)


def receipt_stats(kw=None, from_date=None, to_date=None):
    query = db.session.query(
        Sanbong.id,
        Sanbong.name,
        func.sum(Receipt.price).label('total_revenue')
    ).join(Receipt, Receipt.sanbong_id == Sanbong.id, isouter=True) \
        .filter(Receipt.status == 'Đã thanh toán')

    if from_date:
        query = query.filter(Receipt.created_date >= from_date)
    if to_date:
        query = query.filter(Receipt.created_date <= to_date)

    query = query.group_by(Sanbong.id, Sanbong.name)

    return query.all()
