from django.urls import path
from . import views


urlpatterns = [
	path('', views.fetch_activities, name='get_all_activities'),
	path('add', views.add_activity, name='add_activity'),
	path('remove', views.remove_activity, name='remove_activity'),
	path('update', views.update_activity, name='update_activity'),
]
