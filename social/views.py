# Stdlib
import traceback
from rest_framework.response import Response
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.db import DatabaseError, IntegrityError
from social.serializers import FollowingsSerializer
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

