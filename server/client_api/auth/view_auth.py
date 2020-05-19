import bcrypt
from flask import request, make_response, jsonify

from app import db
from server.client_api.auth.token import encode_auth_token
from http import HTTPStatus
from server.client_api.utils.view_types import AuthorizedView, BaseView
from server.models import User, BlacklistToken


class LoginAPI(BaseView):
    def post(self):
        post_data = request.get_json()
        user = User.query.filter_by(username=post_data.get('username')).first()

        if user and bcrypt.checkpw(post_data.get('password', '').encode('utf-8'), user.password_hash.encode('utf-8')):
            auth_token = encode_auth_token(user.user_id)

            return make_response(jsonify({
                        'auth_token': auth_token.decode()
                    })), HTTPStatus.OK
        else:
            return make_response(jsonify({
                'message': 'User not registered.'
            })), HTTPStatus.NOT_FOUND


class LogoutAPI(AuthorizedView):
    def post(self):
        blacklist_token = BlacklistToken(token=self.get_auth_token())
        db.session.add(blacklist_token)
        db.session.commit()
        return make_response(jsonify({})), HTTPStatus.OK
