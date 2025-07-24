import enum
from rest_framework.response import Response
from social.models import Follower
from user.models import User


class ConnectionActionEnum(enum.Enum):
	FOLLOW = 1
	UNFOLLOW = 2


def connection_update_with_user(user: User, username: str, action=ConnectionActionEnum.FOLLOW):
	follow = action == ConnectionActionEnum.FOLLOW
	if not username:
		return Response({
			'status': False,
			'message': f"Failed to {'follow' if follow else 'unfollow'}, missing valid target username"
		})
	if user.username == username:
		return Response({
			'status': False,
			'message': f"You can't {'follow' if follow else 'unfollow'} yourself"
		})
	try:
		target_user: User = User.objects.only('uid').get(username=username)
	except User.DoesNotExist:
		return Response(
			{
				'status': False,
				'message': f"Failed to {'follow' if follow else 'unfollow'}, target user doesn't exist",
			}
		)
	if follow:
		obj, created = Follower.objects.get_or_create(
			user=user,
			follower=target_user
		)
		if not created:
			return Response({
				'status': True,
				'message': 'You already follow this user',
			})
	else:
		try:
			Follower.objects.only('id').get(user=user, follower=target_user).delete()
		except Follower.DoesNotExist:
			return Response({
				'status': False,
				'message': "You don't follow this user",
			})

	return Response({
		'status': True,
		'message': 'followed' if follow else 'unfollowed',
	})