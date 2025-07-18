from django.contrib.auth.models import AbstractBaseUser, Group, Permission, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from user import managers


class User(AbstractBaseUser, PermissionsMixin):
	uid = models.AutoField(_("uid"), primary_key=True)
	username = models.CharField(_("username"), unique=True, max_length=250)
	email = models.EmailField(_("email"), unique=True, max_length=250)
	password = models.CharField(_("password"), max_length=128)
	is_admin = models.BooleanField(_("is admin"), default=False)
	last_login = models.DateTimeField(_("last login"), blank=True, null=True)
	date_joined = models.DateTimeField(default=timezone.now)

	# Required for PermissionsMixin to work properly with admin
	groups = models.ManyToManyField(
			Group,
			verbose_name='groups',
			blank=True,
			help_text='The groups this user belongs to.',
			related_name='user_set'
	)
	user_permissions = models.ManyToManyField(
			Permission,
			verbose_name=_('user permissions'),
			blank=True,
			help_text=_('Specific permissions for this user.'),
			related_name="custom_user_set"
	)

	USERNAME_FIELD = 'username'
	REQUIRED_FIELDS = ['email']

	objects = managers.UserManager()

	@property
	def is_staff(self):
		return self.is_admin

	@property
	def is_superuser(self):
		return self.is_admin

	def __str__(self):
		return self.username
