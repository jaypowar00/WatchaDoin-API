import uuid
from datetime import timedelta
from django.db import models
from activity.models.sharing import ShareType
from user.models import User


class Activity(models.Model):
	id = models.AutoField(primary_key=True, editable=False)
	name = models.CharField(max_length=100, null=False, blank=False)
	emoji = models.CharField(max_length=50, default="🔮")
	is_builtin = models.BooleanField(default=False)
	user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='activity')
	created_at = models.DateTimeField(auto_now_add=True)


class ActivityTimer(models.Model):
	id = models.AutoField(primary_key=True, editable=False)
	activity = models.ForeignKey(Activity, on_delete=models.CASCADE, related_name='timer')
	duration = models.DurationField(default=timedelta(minutes=10))


class ActivityStatus(models.Model):
	id = models.AutoField(primary_key=True, editable=False)
	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_status')
	activity = models.ForeignKey(Activity, on_delete=models.CASCADE, related_name='activity_status')
	duration = models.DurationField(default=timedelta(minutes=10))
	started_at = models.DateTimeField(auto_now_add=True)
	is_finished = models.BooleanField(default=False)
	share_type = models.CharField(max_length=10, choices=ShareType.choices)
