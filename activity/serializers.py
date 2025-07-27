from rest_framework import serializers
from .models.activity import Activity, ActivityStatus, ActivityTimer


class ActivitySerializer(serializers.ModelSerializer):
	duration = serializers.SerializerMethodField(method_name='get_activity_timers')
	class Meta:
		model = Activity
		fields = ['id', 'name', 'emoji', 'is_builtin', 'user', 'created_at', 'duration']

	@staticmethod
	def get_activity_timers(obj: Activity):
		activity_timers = ActivityTimer.objects.only('duration').filter(activity=obj)
		return [int(timer.duration.total_seconds() // 60) for timer in activity_timers]


class ActivityTimerSerializer(serializers.ModelSerializer):

	class Meta:
		model = ActivityTimer
		fields = ['id', 'duration']


class ActivityStatusSerializer(serializers.ModelSerializer):
	activity_name = serializers.CharField(source='activity.name', read_only=True)
	is_finished = serializers.SerializerMethodField()

	class Meta:
		model = ActivityStatus
		fields = ['id', 'activity_name', 'started_at', 'duration', 'is_finished', 'share_type']

	def get_is_finished(self, obj):
		return obj.is_finished_virtual
