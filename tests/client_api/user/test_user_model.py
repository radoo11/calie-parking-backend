import unittest
import jwt
from app import db, app
from server.client_api.auth.token import encode_auth_token
from server.models import User
from tests.base import BaseTestCase

class TestUserModel(BaseTestCase):
    def test_encode_auth_token(self):
        user = User(
            username='makor',
            password="trys",
            name='Marek Kordy',
            email="johnDoe@wp.pl"
        )
        db.session.add(user)
        db.session.commit()
        auth_token = encode_auth_token(user.user_id)
        self.assertTrue(isinstance(auth_token, bytes))

        decoded_id = jwt.decode(auth_token.decode('utf-8'), app.config.get('SECRET_KEY'))['sub']
        self.assertEqual(user.user_id, decoded_id)

if __name__ == '__main__':
    unittest.main()