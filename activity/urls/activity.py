from django.urls import path
from activity.views import activity


urlpatterns = [
	path('', activity.fetch_activities, name='get_all_activities'),
	path('add', activity.add_activity, name='add_activity'),
	path('remove', activity.remove_activity, name='remove_activity'),
	path('update', activity.update_activity, name='update_activity'),
]
