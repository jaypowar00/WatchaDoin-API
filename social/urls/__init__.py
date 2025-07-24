from django.urls import include, path

urlpatterns = [
	path('connections/', include('social.urls.connections')),
	path('notifications/', include('social.urls.notifications')),
]
