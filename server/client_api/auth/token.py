import datetime
import jwt

from app import app
from server.models import BlacklistToken


def encode_auth_token(user_id):
    payload = {
        'exp': datetime.datetime.utcnow() + app.config.get('TOKEN_DURATION'),
        'iat': datetime.datetime.utcnow(),
        'sub': user_id
    }
    return jwt.encode(
        payload,
        app.config.get('SECRET_KEY'),
        algorithm='HS256'
    )


def check_blacklist(auth_token):
    res = BlacklistToken.query.filter_by(token=str(auth_token)).first()
    if res:
        return True
    else:
        return False