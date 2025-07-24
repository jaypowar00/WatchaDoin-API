from django.urls import path

from social.views import notifications

urlpatterns = [
	path('toggle', notifications.toggle_notifications, name='toggle_notifications'),
]
