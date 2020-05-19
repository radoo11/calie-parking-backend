import datetime
import json
from unittest.mock import patch

from app import db, app
from http import HTTPStatus
from server.models import BlacklistToken
from tests.base import AuthorizedTestCase


def login_user(self, username, password):
    return self.client.post(
        '/auth/login',
        data=json.dumps({
            'username': username,
            'password': password
        }),
        content_type='application/json'
    )

def blacklist_token(auth_token):
    blacklist_token = BlacklistToken(token=auth_token)
    db.session.add(blacklist_token)
    db.session.commit()


class TestAuth(AuthorizedTestCase):
    def test_registered_user_login(self):
        print(datetime.datetime.utcnow())
        with self.client:
            response = login_user(self, self.user.username, self.user_password)
            data = json.loads(response.data.decode())
            self.assertTrue(data['auth_token'])
            self.assertTrue(response.content_type == 'application/json')
            self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_invalid_password(self):
        with self.client:
            self.assert404(login_user(self, self.user.username, 'INVALID_PW'))

    def test_non_registered_user_login(self):
        with self.client:
            response = login_user(self, '+48000000000', '1234')
            self.assertTrue(response.content_type == 'application/json')
            self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_user_status_malformed_bearer_token(self):
        with self.client:
            response = self.client.get(
                '/user/status',
                headers={'Authorization': 'XXX'})
            self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)

    def test_valid_logout(self):
        with self.client:
            response = self.client.post(
                '/auth/logout',
                headers={'Authorization': self.auth_bearer})
            self.assertEqual(response.status_code, HTTPStatus.OK)

    @patch.dict(app.config, {'TOKEN_DURATION': datetime.timedelta(seconds=-1)})
    def test_token_expired(self):
        with self.client:
            resp_login = login_user(self, self.user.username, self.user_password)
            data_login = json.loads(resp_login.data.decode())
            response = self.client.post(
                '/auth/logout',
                headers={'Authorization': 'Bearer ' + data_login['auth_token']})
            self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)

    def test_valid_blacklisted_token_logout(self):
        with self.client:
            blacklist_token(self.auth_token)
            response = self.client.post(
                '/auth/logout',
                headers={'Authorization': self.auth_bearer})
            data = json.loads(response.data.decode())
            self.assertTrue(data['message'] == 'Token blacklisted. Please log in again.')
            self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)

    def test_valid_blacklisted_token_user(self):
        with self.client:
            blacklist_token(self.auth_token)
            response = self.client.get(
                '/user/status',
                headers={'Authorization': self.auth_bearer})
            data = json.loads(response.data.decode())
            self.assertTrue(data['message'] == 'Token blacklisted. Please log in again.')
            self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)
