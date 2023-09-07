from rest_framework import serializers
from accounts.models import User
from favorites.models import FavoriteUser
from profiles.api.serializers import ProfileSerializer

class FavoriteUserSerializer(serializers.ModelSerializer):
    favorite_users = serializers.SerializerMethodField()
    class Meta:
        model = FavoriteUser
        fields = ['id','user','favorite_users']

    def get_favorite_users(self,obj):
        return UserSerializer(instance=obj.favorite_users.all(),many=True,context={"request": self._context['request']}).data

class UserSerializer(serializers.ModelSerializer):
    profile = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = ['id','profile']

    def get_profile(self,obj):
        return ProfileSerializer(instance=obj.profile,context={"request": self._context['request']}).data