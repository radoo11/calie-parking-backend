from flask import request, make_response, jsonify

from app import db
from server.client_api.auth.token import encode_auth_token
from http import HTTPStatus
from server.client_api.utils.view_types import AuthorizedView
from server.models import User, BlacklistToken


class UserStatusAPI(AuthorizedView):
    def get(self):
        user = self.get_current_user()
        if(user.owned_parking_space):
            response = {
                'username': user.username,
                'name': user.name,
                'email': user.email,
                'lottery_priority': user.lottery_priority,
                'registered_on': user.registered_on,
                'owned_parking_space': user.owned_parking_space.space_number
            }
            return make_response(jsonify(response)), HTTPStatus.OK
        else:
            response = {
                'username': user.username,
                'name': user.name,
                'email': user.email,
                'lottery_priority': user.lottery_priority,
                'registered_on': user.registered_on
            }
            return make_response(jsonify(response)), HTTPStatus.OK