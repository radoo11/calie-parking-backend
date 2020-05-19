from flask import Blueprint
from flask_cors import CORS, cross_origin

from server.client_api.auth.view_auth import LoginAPI, LogoutAPI
from server.client_api.auth.view_register import RegisterAPI
from server.client_api.user.view_status import UserStatusAPI
from server.client_api.parking_space.view_parking_space_waive import WaiveParkingSpaceAPI
from server.client_api.parking_space.view_lottery_draw import LotteryDrawApi

register_view = RegisterAPI.as_view('register_view')
login_view = LoginAPI.as_view('login_view')
logout_view = LogoutAPI.as_view('logout_view')
status_view = UserStatusAPI.as_view('status_view')
parking_space_waive_view = WaiveParkingSpaceAPI.as_view('parking_space_waive_view')
lottery_draw_view = LotteryDrawApi.as_view('lottery_draw_view')

client_api_blueprint = Blueprint('client_api', __name__)
CORS(client_api_blueprint)

client_api_blueprint.add_url_rule('/auth/register', methods=['POST'], view_func=register_view, )
client_api_blueprint.add_url_rule('/auth/login', methods=['POST'], view_func=login_view)
client_api_blueprint.add_url_rule('/auth/logout', methods=['POST'], view_func=logout_view)
client_api_blueprint.add_url_rule('/user/status', methods=['GET'], view_func=status_view)
client_api_blueprint.add_url_rule('/parking-space', methods=['POST', 'GET'], view_func=parking_space_waive_view)
client_api_blueprint.add_url_rule('/lottery-draw', methods=['GET'], view_func=lottery_draw_view)
client_api_blueprint.add_url_rule('/lottery-draw/<int:lottery_draw_id>', methods=['PUT'], view_func=lottery_draw_view)

