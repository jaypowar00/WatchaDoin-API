from django.urls import path, include


urlpatterns = [
	path('', include('activity.urls.activity')),
	path('timers/', include('activity.urls.timer')),
]
