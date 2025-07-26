from django.urls import path
from . import views


urlpatterns = [
	path('', views.fetch_activities, name='get_all_activities'),
	path('add', views.add_activity, name='add_activity'),
	path('remove', views.remove_activity, name='remove_activity'),
	path('update', views.update_activity, name='update_activity'),
	path('timers', views.fetch_timers, name='fetch_timers'),
	path('update-timer', views.update_timer, name='update_timer'),
	path('add-timer', views.add_timer, name='add_timer'),
	path('remove-timer', views.remove_timer, name='remove_timer'),
]
