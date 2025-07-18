# Stdlib
import time
import logging
import traceback

# Third-party
import jwt
import redis
from rest_framework.response import Response
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.db.utils import OperationalError as DjangoOperationalError
from psycopg2 import OperationalError as Psycopg2OperationalError

# Project/local
from config import settings
from config.redis_client import redis_client
from config.utils.token_service import generate_access_token, generate_refresh_token


# --------------------------------------
# AUTHENTICATION VIEWS
# --------------------------------------

@api_view(['POST'])
@permission_classes([AllowAny])
def user_signup(request):
    logger = logging.getLogger(__name__)
    email = request.data.get('email')
    username = request.data.get('username')
    password = request.data.get('password')
    missing = [k for k, v in {'email': email, 'username': username, 'password': password}.items() if not v]
    if missing:
        return Response({
            'status': False,
            'message': f"Registration Failed. Missing data for fields: {', '.join(missing)}"
        })
    try:
        User = get_user_model()
        user = User(email=email, username=username)
        user.set_password(password)
        user.save()
        return Response({
            'status': True,
            'message': 'User created!',
            'tokens': {
                'access_token': generate_access_token(user),
                'refresh_token': generate_refresh_token(user),
            },
        })
    except IntegrityError as err:
        err_msg = str(err)
        dup_field = 'email' if 'email' in err_msg else 'username'
        return Response({
            'status': False,
            'message': f'{dup_field} already taken by another user, try again with another {dup_field}',
            'duplicate': dup_field
        })
    except (Psycopg2OperationalError, DjangoOperationalError):
        logger.error("Database error:\n" + traceback.format_exc())
        return Response({
            'status': False,
            'message': 'Database connection lost. Please try again later.'
        })
    except redis.exceptions.ConnectionError:
        logger.error("Redis error:\n" + traceback.format_exc())
        return Response({
            'status': False,
            'message': 'Redis connection lost. Please try again later.'
        })
    except Exception as ex:
        logger.error("Unhandled exception:\n" + traceback.format_exc())
        return Response({
            'status': False,
            'message': f'Unexpected error occurred: {str(ex)}'
        })


@api_view(['POST'])
@authentication_classes([])
def user_login(request):
    required_fields = ['username', 'password']
    missing = [field for field in required_fields if not request.data.get(field)]
    if missing:
        return Response({
            'status': False,
            'message': f'Missing fields: {", ".join(missing)}'
        })
    username = request.data.get('username')
    password = request.data.get('password')
    user = get_user_model().objects.only('uid').get(username=username)
    if not user:
        return Response(
            {
                'status': False,
                'message': 'User does not exist',
            }
        )
    if not user.check_password(password):
        return Response(
            {
                'status': False,
                'message': 'Wrong password',
            }
        )
    access_token = generate_access_token(user)
    refresh_token = generate_refresh_token(user)
    return Response(
        {
            'status': True,
            'message': 'Logged in',
            'access_token': access_token,
            'refresh_token': refresh_token,
        }
    )


@api_view(['POST'])
@authentication_classes([])
@permission_classes([AllowAny])
def user_logout(request):
    authorization_header = request.headers.get('Authorization')
    access_token = None
    refresh_token = request.headers.get('refresh-token')
    payload = None
    refresh_payload = None

    # Step 1: Try decoding access token
    if authorization_header:
        try:
            access_token = authorization_header.split(' ')[1]
            payload = jwt.decode(access_token, settings.SECRET_KEY, algorithms=['HS256'])
        except (jwt.ExpiredSignatureError, jwt.InvalidSignatureError, jwt.DecodeError):
            access_token = None
        except Exception:
            pass

    # Step 2: Try decoding refresh token if present
    if refresh_token:
        try:
            refresh_payload = jwt.decode(refresh_token, settings.REFRESH_SECRET_KEY, algorithms=['HS256'])
        except (jwt.ExpiredSignatureError, jwt.InvalidSignatureError, jwt.DecodeError):
            refresh_token = None
        except Exception:
            pass
    print(f"access_token: {access_token}")
    print(f"refresh_token: {refresh_token}")
    # Step 3: If both are missing or expired
    if not access_token and not refresh_token:
        return Response({
            'status': True,
            'message': 'No valid token found. Possibly already logged out.',
        })

    # Step 4: Check if already blacklisted
    already_blacklisted = False

    if access_token and redis_client.get(access_token):
        already_blacklisted = True
        if refresh_token and not redis_client.get(refresh_token):
            ttl = max(0, refresh_payload['exp'] - int(time.time())) if refresh_payload else 0
            redis_client.setex(refresh_token, ttl, 'blacklisted')

    if refresh_token and redis_client.get(refresh_token):
        already_blacklisted = True
        if access_token and not redis_client.get(access_token):
            ttl = max(0, payload['exp'] - int(time.time())) if payload else 0
            redis_client.setex(access_token, ttl, 'blacklisted')

    if already_blacklisted:
        return Response({'status': True, 'message': 'Already logged out!'})

    # Step 5: Add to Redis blacklist with TTL based on token expiry
    if access_token and payload:
        ttl = max(0, payload['exp'] - int(time.time()))
        redis_client.setex(access_token, ttl, 'blacklisted')

    if refresh_token and refresh_payload:
        ttl = max(0, refresh_payload['exp'] - int(time.time()))
        redis_client.setex(refresh_token, ttl, 'blacklisted')

    return Response({
        'status': True,
        'message': 'Successfully logged out!',
    })


@api_view(['POST'])
@authentication_classes([])
def refresh_token_view(request):
    refresh_token = request.headers.get('refresh-token')
    if not refresh_token:
        return Response({
            'status': False,
            'message': 'Refresh token missing in request',
        })
    try:
        payload = jwt.decode(refresh_token, settings.REFRESH_SECRET_KEY, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        return Response({
            'status': False,
            'message': 'Refresh token expired!',
        })
    except (jwt.InvalidSignatureError, jwt.DecodeError):
        return Response({
            'status': False,
            'message': 'Invalid refresh token!',
        })
    # Check Redis blacklist
    if redis_client.get(refresh_token):
        return Response({
            'status': False,
            'message': 'Refresh token blacklisted!',
        })
    user = get_user_model().objects.only('uid').filter(uid=payload['user_id']).first()
    if user is None:
        return Response({
            'status': False,
            'message': 'User associated with received token does not exists anymore!',
        })
    # Blacklist current refresh token
    ttl = max(0, payload['exp'] - int(time.time())) if (payload and 'exp' in payload) else 0
    redis_client.setex(refresh_token, ttl, 'blacklisted')
    # Generate new tokens
    access_token = generate_access_token(user)
    refresh_token = generate_refresh_token(user)
    return Response({
        'status': True,
        'message': 'Tokens refreshed',
        'access_token': access_token,
        'refresh_token': refresh_token,
    })


# --------------------------------------
# USER MANAGEMENT VIEWS
# --------------------------------------

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_profile(request):
    user = request.user
    return Response({
        'status': True,
        'user': {
            'email': user.email,
            'username': user.username,
            'date_joined': user.date_joined
        }
    })
