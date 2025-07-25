import uuid
from django.db import models
from user.models import User


class ShareType(models.TextChoices):
    FOLLOWERS = 'followers', 'Followers'
    SELF = 'self', 'Only Me'
    PRIVATE = 'private', 'Private List'


class PrivateShareList(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='private_share_list')
    name = models.CharField(max_length=120)

class PrivateShareListMember(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    list = models.ForeignKey(PrivateShareList, on_delete=models.CASCADE, related_name='member')
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='follower')
