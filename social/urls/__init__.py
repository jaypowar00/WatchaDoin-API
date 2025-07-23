from django.urls import include, path

urlpatterns = [
	path('connections/', include('social.urls.connections')),
]
