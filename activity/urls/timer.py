from django.urls import path
from activity.views import timer


urlpatterns = [
	path('', timer.fetch_timers, name='fetch_timers'),
	path('update-timer', timer.update_timer, name='update_timer'),
	path('add-timer', timer.add_timer, name='add_timer'),
	path('remove-timer', timer.remove_timer, name='remove_timer'),
]
