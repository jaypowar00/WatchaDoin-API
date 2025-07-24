# Stdlib
import traceback

# Third-party
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.db import DatabaseError, IntegrityError

# Project/local
from user.models import User
from social.serializers import FollowersSerializer, FollowingsSerializer
from social.utils.connections.connection_update_with_user import connection_update_with_user, ConnectionActionEnum


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def followings_list(request):
	user: User = request.user
	order = '' if request.GET.get('order', '-') == '1' else '-'
	try:
		followings = user.following.select_related('follower').only(
			'id', 'follower_id', 'followed_on', 'notifications_enabled', 'follower__username',
		).order_by(f'{order}followed_on')
		ser_followings = FollowingsSerializer(followings, many=True).data
		return Response({
			'status': True,
			'followings': ser_followings,
		})
	except DatabaseError as err:
		print(f"[-] Database error occurred: {err}")
		print(f"traceback.format_exc(): {traceback.format_exc()}")
		return Response({
			'status': False,
			'message': 'Database error occurred while fetching followings.',
		})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def followers_list(request):
	user: User = request.user
	order = '' if request.GET.get('order', '-') == '1' else '-'
	try:
		followers = user.followers.select_related('user').only(
			'id', 'user_id', 'followed_on', 'user__username',
		).order_by(f'{order}followed_on')
		ser_followers = FollowersSerializer(followers, many=True).data
		return Response({
			'status': True,
			'followers': ser_followers,
		})
	except DatabaseError as err:
		print(f"[-] Database error occurred: {err}")
		print(f"traceback.format_exc(): {traceback.format_exc()}")
		return Response({
			'status': False,
			'message': 'Database error occurred while fetching followers.',
		})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def follow_user(request):
	user: User = request.user
	username = request.data.get('username')
	response: Response = connection_update_with_user(user, username)
	return response


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def unfollow_user(request):
	user: User = request.user
	username = request.data.get('username')
	response: Response = connection_update_with_user(user, username, ConnectionActionEnum.UNFOLLOW)
	return response
