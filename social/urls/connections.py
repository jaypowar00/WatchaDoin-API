from django.urls import path
from social.views import connections

urlpatterns = [
	path('/followings', connections.followings_list, name='followings_list'),
	# path('/followers', connections.followers_list, name='followers_list'),               # TODO 1
    # path('/follow', connections.follow_user, name='follow_user'),                        # TODO 2
	# path('/unfollow', views.unfollow_user, name='unfollow'),                             # TODO 3
]
