from datetime import datetime
from flask import request, make_response, jsonify, json

from app import db
from http import HTTPStatus
from server.client_api.utils.view_types import AuthorizedView
from server.models import User, ParkingSpaceWaive

class WaiveParkingSpaceAPI(AuthorizedView):
    def post(self):
        post_data = request.get_json()
        user = self.get_current_user()

        if user and user.owned_parking_space_id is None:
            return make_response(jsonify({})), HTTPStatus.NOT_FOUND

        else:
            dates = post_data.get('dates')
            if(len(dates) == 0):
                return make_response(jsonify({
                    'message': 'No dates'
                })), HTTPStatus.NOT_FOUND

            for date in dates:
                if not db.session.query(ParkingSpaceWaive.query.filter_by(parking_space_id=user.owned_parking_space_id,
                                                     date=datetime.strptime(date, '%Y-%m-%d').date()).exists()).scalar():
                    waived_parking_space = ParkingSpaceWaive(parking_space_id=user.owned_parking_space_id,
                                                             date=datetime.strptime(date, '%Y-%m-%d').date())
                    db.session.add(waived_parking_space)
                else:
                   return make_response(jsonify({
                       'message': 'Parking space is waived for this date'
                   })), HTTPStatus.METHOD_NOT_ALLOWED

            db.session.commit()

            return make_response(jsonify({
                'message': 'Parking space waived'
            })), HTTPStatus.OK

    def get(self):
        user = self.get_current_user()
        waived_dates_parking_spaces = ParkingSpaceWaive.query.filter_by(
            parking_space_id=user.owned_parking_space_id).all()

        dates = []
        for x in waived_dates_parking_spaces:
            dates.append(str(x.date))

        if waived_dates_parking_spaces:
            return make_response(jsonify({
                'dates': dates
            })), HTTPStatus.OK

        return make_response(jsonify({})), HTTPStatus.NOT_FOUND
