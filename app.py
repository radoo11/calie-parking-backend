import os

from flask import Flask, send_file, send_from_directory
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config.from_object(os.getenv(
    'APP_SETTINGS',
    'config.DevelopmentConfig'
))

db = SQLAlchemy(app)

db.create_all()

# register endpoints
from server.client_api.blueprint import client_api_blueprint
app.register_blueprint(client_api_blueprint)


@app.route('/<path:path>')
def send_static_dir(path):
    app.logger.info(f'matched {path}')
    return send_from_directory('server/static', path)

@app.route('/')
def send_index():
    return send_file('server/static/index.html')


if __name__ == '__main__':
    app.run()
