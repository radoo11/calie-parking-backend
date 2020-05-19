import json

from app import db
from http import HTTPStatus
from tests.base import AuthorizedTestCase

class UserStatusTests(AuthorizedTestCase):
    def test_should_send_required_fields(self):
        with self.client:
            response = self.client.get('/user/status', headers={'Authorization': self.auth_bearer})

            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, HTTPStatus.OK)
            self.assertEqual(data['username'], self.user.username)
            self.assertEqual(data['name'], self.user.name)
            self.assertEqual(data['email'], self.user.email)
