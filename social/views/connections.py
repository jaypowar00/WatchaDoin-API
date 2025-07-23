# Stdlib
import traceback

# Third-party
from rest_framework.response import Response
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.db import DatabaseError, IntegrityError

# Project/local
from social.models import Follower
from social.serializers import FollowersSerializer, FollowingsSerializer
from user.models import User


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def followings_list(request):
	user: User = request.user
	try:
		followings = user.following.select_related('follower').only(
			'id', 'follower_id', 'followed_on', 'follower__username',
		)
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
	try:
		followers = user.followers.select_related('user').only(
			'id', 'user_id', 'followed_on', 'user__username',
		)
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
	if not username:
		return Response({
			'status': False,
			'message': f"Failed to follow, missing valid target username"
		})
	if user.username == username:
		return Response({
			'status': False,
			'message': f"You can't follow yourself"
		})
	try:
		target_user: User = User.objects.only('uid').get(username=username)
	except User.DoesNotExist:
		return Response(
			{
				'status': False,
				'message': "Failed to follow, target user doesn't exist",
			}
		)
	obj, created = Follower.objects.get_or_create(
		user=user,
		follower=target_user
	)
	if not created:
		return Response({
			'status': True,
			'message': 'You already follow this user',
		})

	return Response({
		'status': True,
		'message': 'Successfully followed',
	})
