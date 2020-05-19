from datetime import datetime, timedelta
from http import HTTPStatus
from flask import request, make_response, jsonify, json
import sqlalchemy

from server.client_api.utils.view_types import AuthorizedView
from server.models import User, ParkingSpaceWaive, LotteryDraw
from app import db

class LotteryDrawApi(AuthorizedView):
    def get(self):
        user = self.get_current_user()
        result = db.session.query(LotteryDraw, ParkingSpaceWaive) \
            .filter(LotteryDraw.user_id == user.user_id) \
            .filter(ParkingSpaceWaive.parking_space_waive_id == LotteryDraw.parking_space_waive_id)\
            .filter(ParkingSpaceWaive.date == datetime.utcnow().date() + timedelta(days=1)).first()

        if result:
            (ld, psw) = result
            return make_response(jsonify({
                "lottery_draw_id": ld.lottery_draw_id,
                "parking_space_number": psw.parking_space.space_number,
                "date": psw.date,
                "confirmed_on": ld.confirmed_on
            })), HTTPStatus.OK

        return make_response(jsonify({})), HTTPStatus.NOT_FOUND

    def put(self, lottery_draw_id):
        lottery_draw = LotteryDraw.query.filter_by(lottery_draw_id=lottery_draw_id).first()

        if lottery_draw and lottery_draw.expires_on > datetime.utcnow():
            lottery_draw.confirmed_on = datetime.utcnow()
            db.session.commit()
            return make_response(jsonify({})), HTTPStatus.OK

        return make_response(jsonify({
            'message': 'Parking space expired.'
        })), HTTPStatus.METHOD_NOT_ALLOWED
