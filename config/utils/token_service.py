from datetime import datetime, timedelta, timezone
import jwt
from django.conf import settings
from config.redis_client import redis_client


def generate_access_token(user):
    now = datetime.now(timezone.utc)
    payload = {
        'user_id': user.uid,
        'exp': now + timedelta(days=1),
        'iat': now,
    }
    access_token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
    redis_client.delete(access_token)
    return access_token

def generate_refresh_token(user):
    now = datetime.now(timezone.utc)
    payload = {
        'user_id': user.uid,
        'exp': now + timedelta(days=7),
        'iat': now,
    }
    refresh_token = jwt.encode(payload, settings.REFRESH_SECRET_KEY, algorithm='HS256')
    redis_client.delete(refresh_token)
    return refresh_token
