from server.models import User, ParkingSpaceWaive, LotteryDraw
from datetime import datetime, timedelta
import numpy as np
import random
from sqlalchemy import and_

from app import app, db

def draw_waived_space_when_place_not_confirmed():
    reserve_users = User.query.filter(User.lottery_priority != 1).all()
    reserve_users_id = list(map(lambda a: a.user_id, reserve_users))

    result_not_confirmed_for_tomorrow = db.session.query(LotteryDraw, ParkingSpaceWaive) \
        .filter(ParkingSpaceWaive.date == datetime.utcnow().date() + timedelta(days=1)) \
        .filter(LotteryDraw.confirmed_on == None) \
        .filter(LotteryDraw.parking_space_waive_id == ParkingSpaceWaive.parking_space_waive_id).all()

    if(result_not_confirmed_for_tomorrow):
        lottery_draw_not_confirmed = [x[0] for x in result_not_confirmed_for_tomorrow]

        result = db.session.query(LotteryDraw, ParkingSpaceWaive) \
            .filter(ParkingSpaceWaive.date == datetime.utcnow().date() + timedelta(days=1))\
            .filter(ParkingSpaceWaive.parking_space_waive_id == LotteryDraw.parking_space_waive_id).all()
        if result:
            lottery_draw_for_tomorrow_user_id = [x[0].user_id for x in result]

            diff = set(reserve_users_id) - set(lottery_draw_for_tomorrow_user_id)
            diff = list(diff)

            if lottery_draw_not_confirmed:
                for drawn in lottery_draw_not_confirmed:
                    if diff:
                        drawn_reserve_user = random.choice(diff)
                        diff.remove(drawn_reserve_user)
                        drawn.user_id = drawn_reserve_user
                        drawn.confirmed_on = datetime.utcnow()
                        db.session.add(drawn)
                    else:
                        drawn.confirmed_on = datetime.utcnow()
                        db.session.add(drawn)
                db.session.commit()

def draw_waived_space_for_reserve_users():
    reserve_users_prio2 = User.query.filter(User.lottery_priority == 2).all()
    reserve_users_prio3 = User.query.filter(User.lottery_priority == 3).all()
    waived_parking_spaces = ParkingSpaceWaive.query.filter_by(
        date=datetime.utcnow().date() + timedelta(days=1)).all()

    reserve_users_weighted = 3 * reserve_users_prio2 + 2 * reserve_users_prio3
    if waived_parking_spaces and reserve_users_weighted:
        for space in waived_parking_spaces:
            if len(reserve_users_weighted) > 0:
                drawn_user = np.random.choice(reserve_users_weighted, 1)
                reserve_users_weighted = list(filter(lambda a: a != drawn_user.item(0), reserve_users_weighted))

                if checkIfResultExists(drawn_user.item(0).user_id,
                                       space.parking_space_waive_id) is None:
                    lottery_draw = LotteryDraw(space.parking_space_waive_id, drawn_user.item(0).user_id)
                    db.session.add(lottery_draw)
        db.session.commit()


def checkIfResultExists(user_id, parking_space_waive_id):
    result = db.session.query(LotteryDraw, ParkingSpaceWaive) \
        .filter(LotteryDraw.user_id == user_id) \
        .filter(LotteryDraw.parking_space_waive_id == parking_space_waive_id) \
        .filter(ParkingSpaceWaive.date == datetime.utcnow().date() + timedelta(days=1)).first()
    return result