# Stdlib
import traceback
from datetime import timedelta

# Third-party
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.db import DatabaseError

# Project/local
from activity.models.activity import Activity, ActivityTimer
from activity.serializers import ActivityTimerSerializer
from user.models import User


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def fetch_timers(request):
	user: User = request.user
	name = request.GET.get('name')
	if not name:
		return Response({
			'status': False,
			'message': "Couldn't fetch timers. Missing activity name",
		})
	try:
		activity = Activity.objects.get(user=user, name=name)
	except Activity.DoesNotExist:
		return Response({
			'status': False,
			'message': f"Activity {name} doesn't exist",
		})
	timers = ActivityTimer.objects.filter(activity=activity)
	ser_timers = ActivityTimerSerializer(timers, many=True).data
	return Response({
		'status': True,
		'timers': ser_timers
	})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_timer(request):
	timer_id = request.data.get('id')
	duration = request.data.get('duration')
	# Check for missing fields
	missing = [k for k, v in {'id': timer_id, 'duration': duration}.items() if not v]
	if missing:
		return Response({
			'status': False,
			'message': f"Couldn't update timer. Missing data for fields: {', '.join(missing)}"
		})
	try:
		timer = ActivityTimer.objects.get(id=timer_id)
		if isinstance(duration, str):
			duration = duration.replace(',', '.')
		timer.duration = timedelta(minutes=int(float(duration)))
		timer.save()
		return Response({
			'status': True,
			'message': 'Timer updated.',
		})
	except ActivityTimer.DoesNotExist:
		return Response({
			'status': False,
			'message': f"Timer data doesn't exist",
		})
	except DatabaseError as ex:
		print(ex)
		print(f"traceback: {traceback.format_exc()}")
		return Response({
			'status': False,
			'message': f"Couldn't update timer. Database error: {str(ex)}",
		})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_timer(request):
	user: User = request.user
	name = request.data.get('name')
	duration = request.data.get('duration')
	# Check for missing fields
	missing = [k for k, v in {'name': name, 'duration': duration}.items() if not v]
	if missing:
		return Response({
			'status': False,
			'message': f"Couldn't update timer. Missing data for fields: {', '.join(missing)}"
		})
	if isinstance(duration, str):
		duration = duration.replace(',', '.')
	try:
		activity = Activity.objects.get(user=user, name=name)
		timer = ActivityTimer(activity=activity, duration=timedelta(minutes=int(float(duration))))
		timer.save()
		return Response({
			'status': True,
			'message': 'Timer added.',
		})
	except Activity.DoesNotExist:
		return Response({
			'status': False,
			'message': f"Activity {name} doesn't exist",
		})
	except DatabaseError as ex:
		print(ex)
		print(f"traceback: {traceback.format_exc()}")
		return Response({
			'status': False,
			'message': f"Couldn't add timer. Database error: {str(ex)}",
		})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def remove_timer(request):
	user: User = request.user
	timer_id = request.data.get('id')
	if not timer_id:
		return Response({
			'status': False,
			'message': f"Couldn't remove timer. Missing timer id",
		})
	try:
		ActivityTimer.objects.get(id=timer_id).delete()
		return Response({
			'status': True,
			'message': 'Timer removed.',
		})
	except ActivityTimer.DoesNotExist:
		return Response({
			'status': False,
			'message': f"Couldn't remove timer. Timer doesnt exist",
		})
