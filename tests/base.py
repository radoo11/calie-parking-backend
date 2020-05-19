from flask_testing import TestCase

from app import app, db
from server.client_api.auth.token import encode_auth_token
from tests.client_api.mixins import UserSetupMixin, UserData


class BaseTestCase(TestCase):
    def create_app(self):
        app.config.from_object('config.TestingConfig')
        return app

    def setUp(self):
        db.drop_all()
        db.create_all()
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()


class AuthorizedTestCase(BaseTestCase, UserSetupMixin):
    user = None
    user_password = None
    auth_token = None
    auth_bearer = None

    def setUp(self):
        super().setUp()
        self.user = self.add_user(UserData.user_1)
        self.user.lottery_priority = 1
        self.user_password = UserData.user_1['password']
        self.auth_token = encode_auth_token(self.user.user_id).decode()
        self.auth_bearer = 'Bearer ' + self.auth_token
