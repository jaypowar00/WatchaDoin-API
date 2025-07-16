from django.contrib import admin
from  django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


class UserAdmin(BaseUserAdmin):
	model = User
	list_display = ('username', 'email', 'is_admin', )
	list_filter = ('is_admin', )
	filter_horizontal = ('user_permissions', 'groups')
	fieldsets = [
	    (None, { 'fields': ['username', 'email', 'password']}),
		('Permissions', { 'fields': ['is_admin', 'user_permissions', 'groups']}),
		('Important dates', { 'fields': ['last_login']}),
	]
	add_fieldsets = [
		(None, { 'fields': ['username', 'email', 'password1', 'password2']}),
		('Permissions', { 'fields': ['is_admin', 'user_permissions', 'groups']}),
	]

admin.site.register(User, UserAdmin)
