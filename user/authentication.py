import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from config.redis_client import redis_client
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.authentication import BaseAuthentication

class SafeJWTAuthentication(BaseAuthentication):

    def authenticate(self, request):
        User = get_user_model()
        authorization_header = request.headers.get('Authorization')
        refresh_token = request.headers.get('refresh-token')
        if not authorization_header:
            return None
        try:
            access_token = authorization_header.split(' ')[1].strip()
            payload = jwt.decode(access_token, settings.SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('access token expired!')
        except (jwt.InvalidSignatureError, jwt.DecodeError):
            raise AuthenticationFailed('Invalid token!')
        except IndexError:
            raise AuthenticationFailed('Token prefix missing')
        if redis_client.get(access_token):
            raise AuthenticationFailed("Access token is blacklisted")
        if refresh_token and redis_client.get(refresh_token):
            raise AuthenticationFailed("Refresh token is blacklisted")

        user = User.objects.filter(uid=payload['user_id']).first()
        if user is None:
            raise AuthenticationFailed('User not found')
        print('[+] Access token verified')
        return user, None
