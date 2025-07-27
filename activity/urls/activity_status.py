from django.urls import path
from activity.views import activity_status

urlpatterns = [
	path('', activity_status.fetch_activities, name='fetch_activities'),
	path('start', activity_status.start_activity, name='start_activity'),
	path('finish', activity_status.finish_activity, name='finish_activity'),
]
