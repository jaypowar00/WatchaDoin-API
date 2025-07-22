import uuid
from django.db import models
from user.models import User


class Follower(models.Model):
	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following')
	follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followers')
	notifications_enabled = models.BooleanField(default=True)
	followed_on = models.DateTimeField(auto_now_add=True)
