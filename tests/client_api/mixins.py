
from app import db
from server.models import User, ParkingSpace, LotteryDraw, ParkingSpaceWaive
from datetime import datetime

class ParkingSpaceData:
    parking_1 = {'space_number': 146}
    parking_2 = {'space_number': 147}
    parking_3 = {'space_number': 148}

class ParkingSpaceMixin:
    def add_parking_spaces(self, parking_space):
        db.session.add(ParkingSpace(**parking_space))
        db.session.commit()

class UserData:
    user_1 = {'username': 'username_test', 'password': 'textxx', 'name': 'Doe', 'email': 'john@doe.com'}
    user_2 = {'username': 'test2', 'password': 'textxx', 'name': 'Doe', 'email': 'john@doe.com'}
    user_3 = {'username': 'test3', 'password': 'textxx', 'name': 'Doe', 'email': 'john@doe.com'}
    user_4 = {'username': 'test4', 'password': 'textxx', 'name': 'Doe', 'email': 'john@doe.com'}

class LotteryDrawMixin:
    def add_lottery_draw(self, parking_space_waive_id, user_id):
        lottery_draw_data = {
            'parking_space_waive_id': parking_space_waive_id,
            'user_id': user_id}
        lottery_draw = LotteryDraw(**lottery_draw_data)
        db.session.add(lottery_draw)
        db.session.commit()
        return lottery_draw

    def confirm_lottery_draw(self, lottery_draw_id):
        lottery_draw = LotteryDraw.query.filter(LotteryDraw.lottery_draw_id == lottery_draw_id).first()
        lottery_draw.confirmed_on = datetime.utcnow()
        db.session.commit()


class WaiveParkingSpaceMixin:
    def add_waived_parking_space(self, parking_space_id, date):
        parking_space_waive_data = {'parking_space_id': parking_space_id,
                                    'date': date}
        waive_parking_space = ParkingSpaceWaive(**parking_space_waive_data)
        db.session.add(waive_parking_space)
        db.session.commit()
        return waive_parking_space

class UserSetupMixin:
    def add_user(self, user_data):
        user = User(**user_data)
        db.session.add(user)
        db.session.commit()
        return user


