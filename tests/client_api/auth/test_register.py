import json

import bcrypt

from app import db
from server.models import User
from http import HTTPStatus
from tests.base import BaseTestCase

PASSWORD = 'xxxx'


def register_user(self, username):
    return self.client.post(
        '/auth/register',
        data=json.dumps(dict(
            username=username,
            password=PASSWORD,
            name='John Doe',
            email='john@doe.com'
        )),
        content_type='application/json',
    )


class TestRegister(BaseTestCase):
    def setUp(self):
        super().setUp()

    def test_registration(self):
        with self.client:
            response = register_user(self, 'username_test')
            data = json.loads(response.data.decode())
            self.assertTrue(data['auth_token'])
            self.assertTrue(response.content_type == 'application/json')

            self.assertEqual(response.status_code, HTTPStatus.CREATED)

            # test password hash
            user = User.query.all()[0]
            self.assertTrue(bcrypt.checkpw(PASSWORD.encode('utf-8'), user.password_hash.encode('utf-8')))

    def test_should_respond_409_when_user_registered(self):
        user = User(
            username='username_test',
            password='xxx',
            name='John',
            email='john@doe.com'
        )
        db.session.add(user)
        db.session.commit()

        with self.client:
            response = register_user(self, 'username_test')
            self.assertEqual(response.status_code, HTTPStatus.CONFLICT)
