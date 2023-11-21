from rest_framework import serializers
from notifications.models import Notification,Banner
from profiles.api.serializers import ProfileSerializer

class NotificationSerializer(serializers.ModelSerializer):
    from_profile = serializers.SerializerMethodField()
    class Meta:
        model = Notification
        fields = ['id','from_profile','context','datetime']

    def get_from_profile(self,obj):
        return ProfileSerializer(instance=obj.from_user.profile,context={"request": self._context['request']}).data



class BannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Banner
        fields = ['id', 'title', 'image']

