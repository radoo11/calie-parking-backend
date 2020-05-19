from datetime import datetime
import json

from http import HTTPStatus
from tests.base import AuthorizedTestCase
from tests.client_api.mixins import ParkingSpaceMixin, ParkingSpaceData
from server.models import ParkingSpaceWaive

def waive_parking_space(self, dates):
    return self.client.post(
        '/parking-space',
        data=json.dumps(dates, indent=4, sort_keys=True),
        headers={'Authorization': self.auth_bearer},
        content_type='application/json'
    )

def get_waived_parking_space(self):
    return self.client.get(
        '/parking-space',
        headers={'Authorization': self.auth_bearer},
        content_type='application/json'
    )

class TestParkingSpaceWaive(AuthorizedTestCase, ParkingSpaceMixin):
    def setUp(self):
        super().setUp()
        self.add_parking_spaces(ParkingSpaceData.parking_1)

    def test_user_have_no_parking_space(self):
        with self.client:
            response = waive_parking_space(self, {'dates': ['2019-10-01']})
            self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
            self.assertEqual(self.user.owned_parking_space, None)

    def test_should_respond_200_when_user_has_parking_space(self):
        self.user.owned_parking_space_id = 1
        with self.client:
            response = waive_parking_space(self, {'dates': ['2019-10-01']})
            self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_should_respond_200_when_user_waive_one_parking_and_is_one_record_in_waived(self):
        self.user.owned_parking_space_id = 1
        with self.client:
            response = waive_parking_space(self, {'dates': ['2019-10-01']})
            waived_parking_space = ParkingSpaceWaive.query.filter_by(parking_space_id=1).first()
            self.assertIsNot(waived_parking_space, None)
            self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_should_respond_200_when_user_waive_more_than_one_parking_and_is__more_than_one_record_in_waived(self):
        self.user.owned_parking_space_id = 1
        with self.client:
            response = waive_parking_space(self, {'dates': ['2019-10-01', '2019-10-02']})
            data = json.loads(response.data.decode())
            waived_parking_space = ParkingSpaceWaive.query.filter_by(parking_space_id=1).count()
            self.assertTrue(waived_parking_space > 1)
            self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_should_respond_200_when_user_waive_plane_on_the_same_date_and_should_be_only_one_record(self):
        self.user.owned_parking_space_id = 1
        with self.client:
            response = waive_parking_space(self, {'dates': ['2019-10-01']})
            waived_parking_space = ParkingSpaceWaive.query.filter_by(parking_space_id=1).count()
            self.assertEqual(waived_parking_space, 1)
            self.assertEqual(response.status_code, HTTPStatus.OK)

            response2 = waive_parking_space(self, {'dates': ['2019-10-01']})
            waived_parking_space2 = ParkingSpaceWaive.query.filter_by(
                parking_space_id=1).count()
            self.assertEqual(waived_parking_space2, 1)
            self.assertEqual(response2.status_code, HTTPStatus.METHOD_NOT_ALLOWED)

    def test_should_respond_404_when_user_have_no_waived_spaces(self):
        with self.client:
            response = get_waived_parking_space(self)
            self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_should_respond_200_when_user_have_waived_spaces(self):
        self.user.owned_parking_space_id = 1
        with self.client:
            response_waive = waive_parking_space(self, {'dates': ['2019-10-01', '2019-10-02']})
            self.assertEqual(response_waive.status_code, HTTPStatus.OK)

            response_get_waived = get_waived_parking_space(self)
            self.assertEqual(response_get_waived.status_code, HTTPStatus.OK)
