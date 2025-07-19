from django.contrib import admin
from  django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


class UserAdmin(BaseUserAdmin):
	model = User
	list_display = ('username', 'email', 'is_email_verified', 'is_admin', )
	list_filter = ('is_admin', 'is_email_verified')
	filter_horizontal = ('user_permissions', 'groups')
	fieldsets = [
	    (None, { 'fields': ['username', 'email', 'password', 'is_email_verified']}),
		('Permissions', { 'fields': ['is_admin', 'user_permissions', 'groups']}),
		('Important dates', { 'fields': ['last_login']}),
	]
	add_fieldsets = [
		(None, { 'fields': ['username', 'email', 'password1', 'password2', 'is_email_verified']}),
		('Permissions', { 'fields': ['is_admin', 'user_permissions', 'groups']}),
	]

admin.site.register(User, UserAdmin)
