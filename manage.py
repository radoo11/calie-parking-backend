from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

from app import app, db

migrate = Migrate(app, db)
manager = Manager(app)

# migrations
manager.add_command('db', MigrateCommand)


@manager.command
def create_db():
    """Creates the db tables."""
    db.create_all()


@manager.command
def drop_db():
    """Drops the db tables."""
    db.drop_all()


from server.client_api.parking_space.lottery_draw_func import draw_waived_space_for_reserve_users,\
    draw_waived_space_when_place_not_confirmed

@manager.command
def draw_waived_space_for_reserve_users_main():
    draw_waived_space_for_reserve_users()

@manager.command
def draw_waived_space_for_places_not_confirmed():
    draw_waived_space_when_place_not_confirmed()


if __name__ == '__main__':
    manager.run()
