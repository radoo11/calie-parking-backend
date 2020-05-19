from datetime import datetime, timedelta
from threading import Timer
from server.client_api.parking_space.lottery_draw_func import draw_waived_space_for_reserve_users,\
    draw_waived_space_when_place_not_confirmed

from apscheduler.schedulers.blocking import BlockingScheduler

sched = BlockingScheduler()

@sched.scheduled_job('cron', day_of_week='mon-sun', hour=16)
def draw_waived_space_for_reserve_users():
    draw_waived_space_for_reserve_users()

@sched.scheduled_job('cron', day_of_week='mon-sun', hour=17)
def draw_waived_space_for_places_not_confirmed():
    draw_waived_space_when_place_not_confirmed()

sched.start()