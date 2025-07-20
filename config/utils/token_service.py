from datetime import datetime, timedelta, timezone
import jwt, time
from django.conf import settings
from config.redis_client import redis_client
from config.utils.security import sha256_hash


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

def generate_email_verification_token(username: str):
    payload = {
        'username': sha256_hash(str(username)),
        'exp': int(time.time()) + 60 * 60 * 1,  # expires in 1 hour
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256'), payload['exp']
