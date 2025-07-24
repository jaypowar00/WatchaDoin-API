# Stdlib
import traceback

# Third-party
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.db import DatabaseError, IntegrityError

# Project/local
from user.models import User
from social.models import Follower


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_notifications(request):
	user: User = request.user
	username = request.data.get('username')
	if not username:
		return Response({
			'status': False,
			'message': "Failed to toggle notification. missing username."
		})
	try:
		target_user = User.objects.only('uid').get(username=username)
	except User.DoesNotExist:
		return Response({
			'status': False,
			'message': f"Failed to toggle notification. {username} doesn't exist."
		})
	try:
		followed_user = Follower.objects.only('notifications_enabled').get(user=user.uid, follower=target_user.uid)
	except Follower.DoesNotExist:
		return Response({
			'status': False,
			'message': f"You don't follow {target_user.username}"
		})
	followed_user.notifications_enabled = not followed_user.notifications_enabled
	try:
		followed_user.save()
	except (DatabaseError, IntegrityError) as e:
		print(e)
		print(f"traceback.format_exec(): {traceback.format_exc()}")
		return Response({
			'status': False,
			'message': f"Failed to toggle notifications for {username}"
		})
	return Response({
		'status': True,
		'notification': followed_user.notifications_enabled
	})