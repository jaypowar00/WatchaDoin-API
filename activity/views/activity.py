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
from activity.serializers import ActivitySerializer
from config.utils.validators import validate_max_lengths
from user.models import User


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def fetch_activities(request):
	user: User = request.user
	only = request.GET.get('only', False)
	res_activities = { }
	OWN = 'own'
	INBUILT = 'inbuilt'
	try:
		if only != False:
			only = INBUILT if only == INBUILT else OWN
			if only == 'inbuilt':
				activities = Activity.objects.filter(is_builtin=True).order_by('-created_at')
			else:
				activities = Activity.objects.filter(is_builtin=False, user=user.uid).order_by('name')
			ser_activities = ActivitySerializer(activities, many=True).data
			res_activities[only] = ser_activities
		else:
			user_activities = Activity.objects.filter(is_builtin=False, user=user.uid).order_by('-created_at')
			inbuilt_activities = Activity.objects.filter(is_builtin=True).order_by('name')
			res_activities[OWN] = ActivitySerializer(user_activities, many=True).data
			res_activities[INBUILT]  = ActivitySerializer(inbuilt_activities, many=True).data
	except DatabaseError as ex:
		print(ex)
		print(f"traceback: {traceback.format_exc()}")
		return Response({
			'status': False,
			'message': str(ex),
			'activities': {},
		})
	return Response({
		'status': True,
		'activities': res_activities,
	})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_activity(request):
	user: User = request.user
	name = request.data.get('name')
	emoji = request.data.get('emoji')
	timers = request.data.get('timers')
	# Check for missing fields
	missing = [k for k, v in {'name': name, 'emoji': emoji, 'timers': timers}.items() if not v]
	if missing:
		return Response({
			'status': False,
			'message': f"Couldn't add activity. Missing data for fields: {', '.join(missing)}"
		})
	# Validate lengths
	is_valid, error_response = validate_max_lengths(request.data, { 'name': 100, 'emoji': 25 })
	if not is_valid:
		return error_response
	if not isinstance(timers, list) or len(timers) == 0:
		return Response({
			'status': False,
			'message': "Couldn't add activity. At least one timer is required.",
		})
	try:
		activity, is_created = Activity.objects.get_or_create(name=name, user=user)
		if not is_created:
			return Response({
				'status': False,
				'message': "Activity with this name already exists.",
			})
		activity.emoji = emoji
		activity.save()
		for timer in timers:
			ActivityTimer.objects.get_or_create(activity=activity, duration=timedelta(minutes=timer))
	except DatabaseError as ex:
		print(ex)
		print(f"traceback: {traceback.format_exc()}")
		return Response({
			'status': False,
			'message': f"Couldn't add activity. Database error: {str(ex)}",
		})
	return Response({
		'status': True,
		'message': 'Activity added.',
	})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def remove_activity(request):
	user: User = request.user
	name = request.data.get('name')
	if not name:
		return Response({
			'status': False,
			'message': "Couldn't remove activity. Missing name",
		})
	try:
		Activity.objects.get(name=name, user=user).delete()
	except Activity.DoesNotExist:
		return Response({
			'status': False,
			'message': "You don't have an activity with this name",
		})
	return Response({
		'status': True,
		'message': 'Activity removed.',
	})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_activity(request):
	user: User = request.user
	name = request.data.get('name')
	new_name = request.data.get('new_name')
	emoji = request.data.get('emoji')
	try:
		activity = Activity.objects.get(user=user, name=name)
	except Activity.DoesNotExist:
		return Response({
			'status': False,
			'message': f"Activity {name} doesn't exist",
		})
	if new_name != name and Activity.objects.filter(user=user, name=new_name).exists():
		return Response({
			'status': False,
			'message': f"You already have used {new_name} for another activity.",
		})
	updated = False
	if new_name and new_name != name:
		activity.name = new_name
		updated = True
	if emoji and emoji != activity.emoji:
		activity.emoji = emoji if emoji else activity.emoji
		updated = True
	if updated:
		activity.save()
	return Response({
		'status': True,
		'message': 'Activity updated.',
	})
