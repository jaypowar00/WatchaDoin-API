from django.urls import path
from . import views

urlpatterns = [
	# path('/my-list', views.followings_list, name='friends_list'),                                           # TODO 1
    # path('/add', views.friends_add, name='friends_add'),                                                    # TODO 2
	path('/my-list', views.followings_list, name='friends_list'),
	# path('/remove', views.friends_remove, name='friends_remove'),                                           # TODO 3
	# path('/update-notifications', views.update_friends_notifications, name='update_friends_notifications'), # TODO 4
]

# TODOs, future-ideas
# TODO 1: GET  /my-list: Lists all friends for the user. Used in UI to show social list.
# TODO 2: POST /add: Used to send social requests or directly add friends. Essential for building the social graph.
# TODO 3: POST /remove: Remove a social. Maintains user control over connections.
# TODO 4: POST /update-notifications: Toggle notifications for a social. Allows users to mute/unmute activity notifications from specific friends.