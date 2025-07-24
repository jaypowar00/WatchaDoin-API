# Stdlib
import time
import logging
import traceback

# Third-party
import jwt
import redis
from django.contrib.auth.hashers import make_password
from django.shortcuts import render
from django.utils.http import urlsafe_base64_decode
from rest_framework.response import Response
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.db.utils import OperationalError as DjangoOperationalError
from psycopg2 import OperationalError as Psycopg2OperationalError

# Project/local
from config import settings
from user.models import User
from config.redis_client import redis_client
from config.utils.security import sha256_hash
from config.utils.validators import validate_max_lengths
from config.utils.send_email import send_congratulations_email, send_verification_email
from config.utils.token_service import (generate_access_token,
                                        generate_email_verification_token,
                                        generate_refresh_token)


# --------------------------------------
# AUTHENTICATION VIEWS
# --------------------------------------

@api_view(['POST'])
@permission_classes([AllowAny])
def user_signup(request):
    email = request.data.get('email')
    username = request.data.get('username')
    password = request.data.get('password')
    # Check for missing fields
    missing = [k for k, v in {'email': email, 'username': username, 'password': password}.items() if not v]
    if missing:
        return Response({
            'status': False,
            'message': f"Registration Failed. Missing data for fields: {', '.join(missing)}"
        })
    # Validate lengths
    is_valid, error_response = validate_max_lengths(request.data, {
        'email': 250, 'username': 250, 'password': 128
    })
    if not is_valid:
        return error_response
    try:
        if User.objects.filter(username=username).exists():
            return Response({
                'status': False,
                'message': f"Username {username} is already taken."
            })
        elif User.objects.filter(email=email).exists():
            return Response({
                'status': False,
                'message': f"Email {email} is already registered."
            })
        print(f"[+] User {username} initiated account creation.")
        token, exp = generate_email_verification_token(username)
        ttl = max(0, exp - int(time.time()))
        redis_client.setex(f'{sha256_hash(username)}_pass', ttl, make_password(password))
        redis_client.setex(f'{sha256_hash(username)}_email', ttl, email)
        send_verification_email(username, email, token)
        return Response({
            'status': True,
            'message': 'Verification email sent. (verification link expires in 1 hour)',
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
        print("Database error:\n" + traceback.format_exc())
        return Response({
            'status': False,
            'message': 'Database connection lost. Please try again later.'
        })
    except redis.exceptions.ConnectionError:
        print("Redis error:\n" + traceback.format_exc())
        return Response({
            'status': False,
            'message': 'Redis connection lost. Please try again later.'
        })
    except Exception as ex:
        print("Unhandled exception:\n" + traceback.format_exc())
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
    try:
        user = get_user_model().objects.only('uid').get(username=username)
    except User.DoesNotExist:
        return Response(
            {
                'status': False,
                'message': 'User not found',
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
    # Step 3: If both are missing or expired
    if not access_token and not refresh_token:
        print('[+] No valid token found. Possibly already logged out')
        return Response({
            'status': True,
            'message': 'Logged out',
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
        print("[+] Already logged out")
    else:
        # Step 5: Add to Redis blacklist with TTL based on token expiry
        if access_token and payload:
            ttl = max(0, payload['exp'] - int(time.time()))
            redis_client.setex(access_token, ttl, 'blacklisted')

        if refresh_token and refresh_payload:
            ttl = max(0, refresh_payload['exp'] - int(time.time()))
            redis_client.setex(refresh_token, ttl, 'blacklisted')

    return Response({
        'status': True,
        'message': 'Logged out',
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
    try:
        user = get_user_model().objects.only('uid').get(uid=payload['user_id'])
    except User.DoesNotExist:
        return Response({
            'status': False,
            'message': 'No user associated with received credentials',
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


def verify_email_view(request):
    uidb64 = request.GET.get('uid')
    token = request.GET.get('token')
    if token and redis_client.get(token):
        return render(request, 'user/verification_failed.html', {
            'reason': 'Invalid verification link',
        })
    if not token or not uidb64:
        return render(request, 'user/verification_failed.html', {
            'reason': 'Missing verification data',
        })
    try:
        username = urlsafe_base64_decode(uidb64).decode()

    except (TypeError, ValueError, OverflowError):
        print(f"[-] Verification failed for uid={uidb64}")
        return render(request, 'user/verification_failed.html', {
            'reason': 'Invalid verification link.',
        })

    try:
        # Check if uidb64 and token data aligns to avoid any invalid request attempts
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        if payload['username'] != sha256_hash(username):
            return render(request, 'user/verification_failed.html', {
                'reason': 'Invalid verification link.',
            })
        if User.objects.filter(username=username).exists():
            return render(request, 'user/verification_failed.html', {
                'reason': 'Account already exists or link was reused',
            })
        password = redis_client.get(f"{sha256_hash(username)}_pass")
        email = redis_client.get(f"{sha256_hash(username)}_email")
        if not email or not password:
            return render(request, 'user/verification_failed.html', {
                'reason': 'The verification link has expired or is no longer valid.',
            })
        # Create User
        user = User(
            username=username,
            email=email,
            password=password,
            is_email_verified=True,
        )
        user.save()
        print(f"[✓] Email verified for {user.uid}")
        redis_client.delete(f"{sha256_hash(username)}_pass")
        redis_client.delete(f"{sha256_hash(username)}_email")
        ttl = max(0, payload['exp'] - int(time.time()))
        redis_client.setex(token, ttl, 'blacklisted')
        send_congratulations_email(user)
        return render(request, 'user/verification_success.html')
    except Exception as ex:
        print(f"traceback: {traceback.format_exc()}")
        return render(request, 'user/verification_failed.html', {
            'reason': 'Expired or invalid verification data.',
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
            'is_email_verified': user.is_email_verified,
            'date_joined': user.date_joined
        }
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def user_update(request):
    user = request.user
    # Validate lengths
    is_valid, error_response = validate_max_lengths(request.data, {
        'email': 250, 'username': 250, 'password': 128
    })
    if not is_valid:
        return error_response
    email = request.data.get('email', None)
    username = request.data.get('username', None)
    password = request.data.get('password', None)
    email = email if email and email != user.email else None
    username = username if username and username != user.username else None
    if email:
        user.email = email
    if username:
        user.username = username
    if password:
        user.set_password(password)
    if any([email, username, password]):
        try:
            user.save()
        except IntegrityError as err:
            err_msg = str(err)
            dup_field = 'email' if 'email' in err_msg else 'username'
            return Response({
                'status': False,
                'message': f'{dup_field} already taken by another user, try again with another {dup_field}',
                'duplicate': dup_field
            })
        except (Psycopg2OperationalError, DjangoOperationalError):
            print("Database error:\n" + traceback.format_exc())
            return Response({
                'status': False,
                'message': 'Database connection lost. Please try again later.'
            })
    print(f" [+] User {user.uid} updated account info.")
    return Response({
        'status': True,
        'message': 'User updated',
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def user_delete(request):
    try:
        uid = request.user.uid
        request.user.delete()
        print(f" [+] User {uid} deleted their account.")
        return Response({
            'status': True,
            'message': 'User deleted',
        })
    except Exception as err:
        print("Unhandled exception: %s", err)
        return Response({
            'status': False,
            'message': str(err),
        })
