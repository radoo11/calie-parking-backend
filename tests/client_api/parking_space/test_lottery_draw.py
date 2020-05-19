import json

from http import HTTPStatus
from tests.base import AuthorizedTestCase
from tests.client_api.mixins import ParkingSpaceMixin, ParkingSpaceData, LotteryDrawMixin, \
    WaiveParkingSpaceMixin, UserData
from server.models import ParkingSpaceWaive, LotteryDraw
from server.client_api.parking_space.lottery_draw_func import draw_waived_space_for_reserve_users, \
    draw_waived_space_when_place_not_confirmed
from datetime import datetime, timedelta


def check_lottery_draw(self):
    return self.client.get(
        '/lottery-draw',
        headers={'Authorization': self.auth_bearer},
        content_type='application/json'
    )

def confirm_loterry_draw(self, lottery_draw_id):
    return self.client.put(
        '/lottery-draw/' + str(lottery_draw_id),
        headers={'Authorization': self.auth_bearer},
        content_type='application/json'
    )

class TestLotteryDraw(AuthorizedTestCase, LotteryDraw, ParkingSpaceMixin, WaiveParkingSpaceMixin, LotteryDrawMixin):
    def setUp(self):
        super().setUp()
        self.add_parking_spaces(ParkingSpaceData.parking_1)
        self.add_parking_spaces(ParkingSpaceData.parking_2)
        self.add_parking_spaces(ParkingSpaceData.parking_3)

    def setUpAdditionalUsers(self):
        user1 = self.add_user(UserData.user_2)
        user1.set_lottery_priority(2)
        user2 = self.add_user(UserData.user_3)
        user3 = self.add_user(UserData.user_4)
        user2.set_lottery_priority(2)
        user3.set_lottery_priority(3)

    def test_no_waived_parking_space_to_draw(self):
        draw_waived_space_for_reserve_users()
        lottery_draw = LotteryDraw.query.all()
        self.assertEqual(lottery_draw, [])

    def test_one_parking_space_waived_for_reserve_user(self):
        self.setUpAdditionalUsers()
        self.add_waived_parking_space(1, datetime.utcnow().date() + timedelta(days=1))
        draw_waived_space_for_reserve_users()
        lottery_draw = LotteryDraw.query.all()
        self.assertTrue(len(lottery_draw) == 1)
        self.assertEqual(lottery_draw[0].parking_space_waive.parking_space_waive_id, 1)

    def test_three_parking_space_waived_for_reserve_users(self):
        self.setUpAdditionalUsers()
        self.add_waived_parking_space(1, datetime.utcnow().date() + timedelta(days=1))
        self.add_waived_parking_space(2, datetime.utcnow().date() + timedelta(days=1))
        self.add_waived_parking_space(3, datetime.utcnow().date() + timedelta(days=1))
        draw_waived_space_for_reserve_users()
        lottery_draw = LotteryDraw.query.all()
        self.assertTrue(len(lottery_draw) == 3)

    def test_one_parking_space_waived_for_reserve_users_on_next_day(self):
        self.setUpAdditionalUsers()
        self.add_waived_parking_space(1, datetime.utcnow().date() + timedelta(days=1))
        self.add_waived_parking_space(2, datetime.utcnow().date() + timedelta(days=2))
        draw_waived_space_for_reserve_users()
        lottery_draw = LotteryDraw.query.all()
        self.assertTrue(len(lottery_draw) == 1)

    def test_request_user_drawn_parking_space_correctly(self):
        ps = self.add_waived_parking_space(1, datetime.utcnow().date() + timedelta(days=1))
        lottery_draw = self.add_lottery_draw(parking_space_waive_id=ps.parking_space_waive_id,
                                             user_id=self.user.user_id)
        with self.client:
            response = check_lottery_draw(self)
            data = json.loads(response.data.decode())
            self.assertTrue(data["lottery_draw_id"] == lottery_draw.lottery_draw_id)
            self.assertTrue(data["parking_space_number"] == ps.parking_space.space_number)
            self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_request_user_have_no_lottery_draw(self):
        with self.client:
            response = check_lottery_draw(self)
            self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_user_confirm_parking_space_in_time(self):
        ps = self.add_waived_parking_space(1, datetime.utcnow().date() + timedelta(days=1))
        lottery_draw = self.add_lottery_draw(parking_space_waive_id=ps.parking_space_waive_id,
                                             user_id=self.user.user_id)
        lottery_draw.created_on = datetime.utcnow()
        lottery_draw.expires_on = datetime.utcnow() + timedelta(hours=3)

        with self.client:
            response = confirm_loterry_draw(self, lottery_draw.lottery_draw_id)
            self.assertIsNot(lottery_draw.confirmed_on, None)
            self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_user_confirm_parking_space_after_time(self):
        ps = self.add_waived_parking_space(1, datetime.utcnow().date() + timedelta(days=1))
        lottery_draw = self.add_lottery_draw(parking_space_waive_id=ps.parking_space_waive_id,
                                             user_id=self.user.user_id)
        lottery_draw.created_on = datetime.utcnow() - timedelta(hours=3)
        lottery_draw.expires_on = datetime.utcnow() - timedelta(seconds=1)

        with self.client:
            response = confirm_loterry_draw(self, lottery_draw.lottery_draw_id)
            self.assertIs(lottery_draw.confirmed_on, None)
            self.assertEqual(response.status_code, HTTPStatus.METHOD_NOT_ALLOWED)

    def test_second_lottery_draw_doesnt_change_drawn_users(self):
        self.setUpAdditionalUsers()
        self.add_waived_parking_space(1, datetime.utcnow().date() + timedelta(days=1))
        self.add_waived_parking_space(2, datetime.utcnow().date() + timedelta(days=1))
        draw_waived_space_for_reserve_users()
        lottery_draw = LotteryDraw.query.all()
        lottery_draw_user_1 = lottery_draw[0].user_id
        lottery_draw_user_2 = lottery_draw[1].user_id
        draw_waived_space_for_reserve_users()
        lottery_draw = LotteryDraw.query.all()
        self.assertEqual(lottery_draw_user_1, lottery_draw[0].user_id)
        self.assertEqual(lottery_draw_user_2, lottery_draw[1].user_id)

    def test_second_lottery_draw_not_drawn_confirmed_place(self):
        user1 = self.add_user(UserData.user_2)
        self.add_waived_parking_space(1, datetime.utcnow().date() + timedelta(days=1))
        lottery_draw_1 = self.add_lottery_draw(1, 2)
        self.confirm_lottery_draw(lottery_draw_id=lottery_draw_1.lottery_draw_id)
        draw_waived_space_when_place_not_confirmed()
        lottery_draw_2 = LotteryDraw.query.all()
        self.assertTrue(len(lottery_draw_2) == 1)
        self.assertEqual(lottery_draw_1.user_id, lottery_draw_2[0].user_id)

    def test_second_user_drawn_not_confirmed_place_in_second_lottery_draw(self):
        user1 = self.add_user(UserData.user_2)
        user2 = self.add_user(UserData.user_3)
        self.add_waived_parking_space(1, datetime.utcnow().date() + timedelta(days=1))
        lottery_draw_1 = self.add_lottery_draw(1, 2)
        draw_waived_space_when_place_not_confirmed()
        lottery_draw_2 = LotteryDraw.query.all()
        self.assertTrue(len(lottery_draw_2) == 1)
        self.assertEqual(lottery_draw_2[0].user_id, user2.user_id)

    def test_second_lottery_draw_confirmed_place_when_no_reserve_users(self):
        user1 = self.add_user(UserData.user_2)
        self.add_waived_parking_space(1, datetime.utcnow().date() + timedelta(days=1))
        lottery_draw_1 = self.add_lottery_draw(1, 2)
        draw_waived_space_when_place_not_confirmed()
        lottery_draw_2 = LotteryDraw.query.all()
        self.assertIsNot(lottery_draw_2[0].confirmed_on, None)







