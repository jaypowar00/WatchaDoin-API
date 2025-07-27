# Stdlib
import traceback
from datetime import timedelta
from dateutil.parser import parse, ParserError

# Third-party
from django.db import DatabaseError
from django.db.models import F
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes

# Project/local
from user.models import User
from social.models import Follower
from activity.models.sharing import ShareType
from activity.models.activity import Activity, ActivityStatus
from activity.serializers import ActivityStatusSerializer


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
	ActivityStatus.objects.filter(
		user=user,
		activity=activity,
		is_finished=False,
		started_at__lt=timezone.now() - F('duration')
	).update(is_finished=True)
	temp_activity_status = ActivityStatus.objects.filter(user=user, activity=activity, is_finished=False)
	if temp_activity_status.exists():
		return Response({
			'status': False,
			'message': "This activity is currently ongoing",
		})
	# Parse ISO datetime string to timezone-aware datetime object
	try:
		started_at = parse(start)
	except ParserError as ex:
		started_at = timezone.now()
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
		activity_status = ActivityStatus.objects.only('started_at', 'duration',
		                                              'is_finished').get(pk=activity_status_id)
		if activity_status.is_finished:
			return Response({
				'status': True,
				'message': "Activity is already finished"
			})
		elapsed = timezone.now() - activity_status.started_at
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


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def fetch_activities(request):
	user: User = request.user
	state = request.GET.get('state')
	uid = request.GET.get('uid')
	state = 'ongoing' if state == 'ongoing' else 'finished' if state else 'both'
	activities = {}
	try:
		if uid:
			target_user = User.objects.get(uid=uid)
			if not Follower.objects.filter(user=user, follower=target_user).exists():
				return Response({
					'status': False,
					'message': "Couldn't fetch activities. You don't follow this user"
				})
			user = target_user
		ActivityStatus.objects.filter(
			user=user,
			is_finished=False,
			started_at__lt=timezone.now() - F('duration')
		).update(is_finished=True)
		if state != 'both':
			activity_statuses = (ActivityStatus.objects
			                     .only('id', 'activity__name', 'started_at',
			                           'duration', 'is_finished', 'share_type')
			                     .filter(user=user, is_finished=False if state == 'ongoing' else True)
			                     .order_by('-started_at'))
			if state == "ongoing":
				activity_statuses = [a for a in activity_statuses if not a.is_finished_virtual]
			ser_activity_statuses = ActivityStatusSerializer(activity_statuses, many=True).data
			activities[state] = ser_activity_statuses
		else:
			ongoing_activities = (ActivityStatus.objects
			                     .only('id', 'activity__name', 'started_at',
			                           'duration', 'is_finished', 'share_type')
			                     .filter(user=user, is_finished=False)
			                     .order_by('-started_at'))
			finished_activities = (ActivityStatus.objects
			                      .only('id', 'activity__name', 'started_at',
			                            'duration', 'is_finished', 'share_type')
			                      .filter(user=user, is_finished=True)
			                      .order_by('-started_at'))
			ser_ongoing_activities = ActivityStatusSerializer(ongoing_activities, many=True).data
			ser_finished_activities = ActivityStatusSerializer(finished_activities, many=True).data
			activities['ongoing'] = ser_ongoing_activities
			activities['finished'] = ser_finished_activities
		return Response({
			'status': True,
			'activities': activities
		})
	except User.DoesNotExist:
		return Response({
			'status': False,
			'message': "Couldn't fetch activities. User doesn't exist"
		})
	except DatabaseError as ex:
		print(ex)
		print(f"traceback.format_exc(): {traceback.format_exc()}")
		return Response({
			'status': False,
			'message': f"Couldn't fetch activities. Database error {ex}",
		})
