import jwt
from flask import request, make_response, jsonify, g
from flask.views import MethodView

from app import app
from server.client_api.auth.token import check_blacklist
from server.models import User
from http import HTTPStatus


def log_request_response(view_fun):
    def decorator(*args, **kwargs):
        app.logger.info(f'Request - path: {request.path}, method: {request.method}, data: {request.data}, headers: {str(request.headers).encode("utf-8")}')

        data, status = view_fun(*args, **kwargs)

        try:
            app.logger.info(f'Response - status: {status}, data: {data.data}')
        except Exception:
            app.logger.info(f'Response - status: {status}, data: {data}')

        return data, status

    return decorator


def user_authorization_required(view_fun):
    def decorator(*args, **kwargs):
        try:
            auth_header = request.headers.get('Authorization', '')
            auth_token = auth_header.split(' ')[1]
            payload = jwt.decode(auth_token, app.config.get('SECRET_KEY'))

            if check_blacklist(auth_token):
                return make_response(jsonify({'message': 'Token blacklisted. Please log in again.'})), HTTPStatus.UNAUTHORIZED
        except jwt.ExpiredSignatureError:
            return make_response(jsonify({'message': 'Signature expired. Please log in again.'})), HTTPStatus.UNAUTHORIZED
        except (jwt.InvalidTokenError, IndexError) :
            return make_response(jsonify({'message': 'Invalid token. Please log in again.'})), HTTPStatus.UNAUTHORIZED

        g.auth_token = auth_token
        g.user_id = payload['sub']
        return view_fun(*args, **kwargs)

    return decorator


class BaseView(MethodView):
    decorators = [log_request_response]


class AuthorizedView(BaseView):
    decorators = [user_authorization_required, log_request_response]

    def get_auth_token(self):
        return g.auth_token

    def get_user_id(self):
        return g.user_id

    def get_current_user(self):
        return User.query.filter_by(user_id=self.get_user_id()).first()
