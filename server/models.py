from datetime import datetime, timedelta

import bcrypt
from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import relationship

from app import app, db

LOTTERY_DRAW_HOURS = 3

class User(db.Model):
    __tablename__ = "users"

    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String, unique=True, index=True, nullable=False)
    password_hash = db.Column(db.String, nullable=False)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)
    lottery_priority = db.Column(db.Integer, nullable=False, default=2)
    registered_on = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    owned_parking_space_id = db.Column(db.Integer, db.ForeignKey('parking_spaces.parking_space_id'), nullable=True)

    owned_parking_space = db.relationship("ParkingSpace", uselist=False)

    def __init__(self, username, password, name, email):
        super().__init__()

        self.username = username
        self.set_password(password)
        self.name = name
        self.email = email

    def set_lottery_priority(self, lottery_priority):
        self.lottery_priority = lottery_priority

    def set_password(self, pw):
        pwhash = bcrypt.hashpw(pw.encode('utf8'), bcrypt.gensalt())
        self.password_hash = pwhash.decode('utf8')


class BlacklistToken(db.Model):
    __tablename__ = 'blacklist_tokens'

    token = db.Column(db.String, primary_key=True)
    blacklisted_on = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


class ParkingSpace(db.Model):
    __tablename__ = "parking_spaces"

    parking_space_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    space_number = db.Column(db.Integer, nullable=False)

    def __init__(self, space_number):
        super().__init__()

        self.space_number = space_number

class ParkingSpaceWaive(db.Model):
    __tablename__ = "parking_space_waives"

    __table_args__ = (
        db.UniqueConstraint('parking_space_id', 'date', name='unique_parking_space_date'),
    )

    parking_space_waive_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    parking_space_id = db.Column(db.Integer, db.ForeignKey('parking_spaces.parking_space_id'), nullable=False)
    date = db.Column(db.Date, nullable=False)

    created_on = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    parking_space = db.relationship("ParkingSpace", uselist=False)

    def __init__(self, parking_space_id, date):
        super().__init__()

        self.parking_space_id = parking_space_id
        self.date = date


class LotteryDraw(db.Model):
    __tablename__ = "lottery_draws"

    __table_args__ = (
        db.UniqueConstraint('parking_space_waive_id', 'user_id', name='unique_waived_parking_space_user'),
    )

    lottery_draw_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    parking_space_waive_id = db.Column(db.Integer, db.ForeignKey('parking_space_waives.parking_space_waive_id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)

    created_on = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    expires_on = db.Column(db.DateTime, nullable=False,
                           default=datetime.utcnow()+timedelta(hours=LOTTERY_DRAW_HOURS))
    confirmed_on = db.Column(db.DateTime, nullable=True)

    parking_space_waive = db.relationship("ParkingSpaceWaive", uselist=False)
    user = db.relationship("User", uselist=False)

    def __init__(self, parking_space_waive_id, user_id):
        super().__init__()

        self.parking_space_waive_id = parking_space_waive_id
        self.user_id = user_id
