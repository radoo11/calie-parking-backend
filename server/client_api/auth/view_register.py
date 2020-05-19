from flask import request, make_response, jsonify

from app import db
from server.client_api.auth.token import encode_auth_token
from http import HTTPStatus
from server.client_api.utils.view_types import BaseView
from server.models import User

class RegisterAPI(BaseView):
    def post(self):
        post_data = request.get_json()

        if User.query.filter_by(username=post_data.get('username')).first():
            return make_response(jsonify({
                        'message': 'User already exists.',
                    })), HTTPStatus.CONFLICT

        user = User(
            username=post_data.get('username'),
            password=post_data.get('password'),
            name=post_data.get('name'),
            email=post_data.get('email')
        )
        db.session.add(user)
        db.session.commit()

        return make_response(jsonify({
            'auth_token': encode_auth_token(user.user_id).decode()
        })), HTTPStatus.CREATED
