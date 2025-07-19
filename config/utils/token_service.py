from datetime import datetime, timedelta, timezone
import jwt, time
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

def generate_email_verification_token(user):
    payload = {
        'user_id': str(user.uid),
        'username': str(user.username),
        'email': str(user.email),
        'password': str(user.password),
        'exp': int(time.time()) + 60 * 60 * 24,  # expires in 24 hours
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
