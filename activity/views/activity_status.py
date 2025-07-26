# Stdlib
import time
import traceback
from datetime import timedelta
from dateutil.parser import parse, ParserError

# Third-party
from django.db import DatabaseError
from rest_framework.utils import timezone
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes

# Project/local
from activity.models.sharing import ShareType
from activity.models.activity import Activity, ActivityStatus, ActivityTimer
from user.models import User


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start_activity(request):
	user = request.user
	activity_id = request.data.get('activity_id')
	duration = request.data.get('duration')
	start = request.data.get('start')
	share_type = str(request.data.get('share_type')).lower()
	# Check for missing fields
	missing = [k for k, v in {'activity_id': activity_id, 'duration': duration, 'start': start}.items() if not v]
	if missing:
		return Response({
			'status': False,
			'message': f"Couldn't start activity. Missing data for fields: {', '.join(missing)}"
		})
	try:
		activity = Activity.objects.get(pk=activity_id)
	except Activity.DoesNotExist:
		return Response({
			'status': False,
			'message': "Couldn't start activity. Activity doesnt exists"
		})
	if ActivityStatus.objects.filter(activity=activity, user=user, is_finished=False).exists():
		return Response({
			'status': False,
			'message': "This activity is currently ongoing",
		})
	# Parse ISO datetime string to timezone-aware datetime object
	try:
		started_at = parse(start)
	except ParserError as ex:
		started_at = timezone.datetime.now()
	share_type = ShareType.FOLLOWERS if share_type not in ShareType.values else share_type
	try:
		activity_status = ActivityStatus(
			user=user,
			activity=activity,
			duration=timedelta(minutes=duration),
			started_at=started_at,
			share_type=share_type,
		)
		activity_status.save()
	except DatabaseError as ex:
		print(ex)
		print(f"traceback.format_exc(): {traceback.format_exc()}")
		return Response({
			'status': False,
			'message': f"Couldn't start activity. Database error {ex}",
		})
	return Response({
		'status': True,
		'message': "Activity started"
	})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def finish_activity(request):
	user: User = request.user
	activity_status_id = request.data.get('act_status_id')
	if not activity_status_id:
		return Response({
			'status': False,
			'message': "Couldn't finish activity. missing activity_status_id"
		})
	try:
		activity_status = ActivityStatus.objects.only('started_at', 'duration',).get(pk=activity_status_id)
		elapsed = timezone.datetime.now() - activity_status.started_at
		if elapsed < activity_status.duration:
			activity_status.duration = elapsed
		activity_status.is_finished = True
		activity_status.save()
		return Response({
			'status': True,
			'message': "Activity finished"
		})
	except ActivityStatus.DoesNotExist:
		return Response({
			'status': False,
			'message': "Couldn't finish activity. Activity status doesnt exist"
		})
	except DatabaseError as ex:
		print(ex)
		print(f"traceback.format_exc(): {traceback.format_exc()}")
		return Response({
			'status': False,
			'message': f"Couldn't finish activity. Database error {ex}",
		})
