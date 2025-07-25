from rest_framework import serializers
from .models.activity import Activity, ActivityTimer


class ActivitySerializer(serializers.ModelSerializer):
	duration = serializers.SerializerMethodField(method_name='get_activity_timers')
	class Meta:
		model = Activity
		fields = ['id', 'name', 'emoji', 'is_builtin', 'user', 'created_at', 'duration']

	@staticmethod
	def get_activity_timers(obj: Activity):
		activity_timers = ActivityTimer.objects.only('duration').filter(activity=obj)
		return [int(timer.duration.total_seconds() // 60) for timer in activity_timers]

