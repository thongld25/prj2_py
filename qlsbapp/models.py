from sqlalchemy import Column, Integer, String, Float, Enum, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from qlsbapp import db, app
from datetime import datetime
from flask_login import UserMixin
from enum import Enum as UserEnum


class Sanbong(db.Model):
    __tablename__ = 'sanbong'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    price = Column(Float, default=0)
    image = Column(String(100))
    active = Column(Boolean, default=True)
    created_date = Column(DateTime, default=datetime.now())
    receipts = relationship('Receipt', backref='sanbong', lazy=True)


    def __str__(self):
        return self.name


class UserRole(UserEnum):
    ADMIN = 1
    USER = 2

class User(db.Model, UserMixin):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    username = Column(String(50), nullable=False, unique=True)
    password = Column(String(50), nullable=False)
    avatar = Column(String(100))
    email = Column(String(50))
    active = Column(Boolean, default=True)
    joined_date = Column(DateTime, default=datetime.now())
    user_role = Column(Enum(UserRole), default=UserRole.USER)
    receipts = relationship('Receipt', backref='user', lazy=True)

    def __str__(self):
        return self.name

class Receipt(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    created_date = Column(DateTime, default=datetime.now())
    user_id = Column(Integer, ForeignKey(User.id), nullable=False)
    sanbong_id = Column(Integer, ForeignKey(Sanbong.id), nullable=False)
    time_play = Column(DateTime)

if __name__ == '__main__':

    # print("XXXX")
    with app.app_context():
        db.create_all()
    # print("Created DB!")
    # c1 = Category(name='San 5')
    # c2 = Category(name='San 7')
    #
    # db.session.add(c1)
    # db.session.add(c2)
    #
    # db.session.commit()
    # sanbongs = [{
    #       "id": 1,
    #       "name": "San bong so 3",
    #       "price": 500000,
    #       "image": "images/anh1.jpg"
    #     }, {
    #       "id": 2,
    #       "name": "San bong so 4",
    #       "price": 500000,
    #       "image": "images/anh2.jpg"
    #     }]
    # with app.app_context():
    #     for sb in sanbongs:
    #         sbong = Sanbong(name=sb['name'], price=sb['price'], image=sb['image'])
    #
    #         db.session.add(sbong)
    #
    #     db.session.commit()

