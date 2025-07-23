from rest_framework import serializers

from social.models import Follower


class FollowingsSerializer(serializers.ModelSerializer):
    follower_username = serializers.CharField(source='follower.username', read_only=True)

    class Meta:
        model = Follower
        fields = ['id', 'follower_id', 'followed_on', 'follower_username']


class FollowersSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Follower
        fields = ['id', 'user_id', 'followed_on', 'user_username']