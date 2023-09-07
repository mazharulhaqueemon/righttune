from rest_framework import serializers
from profiles.models import Profile

class SearchSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    is_favorite = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = ['id','user','is_favorite','full_name','slug','email','profile_image','cover_image','birthday','gender','registered_date','updated_date']

    def get_user(self,obj):
        user_obj = obj.user
        return {
            'uid': user_obj.id,
            'phone': user_obj.phone
        }

    def get_is_favorite(self,obj):
        try:
            return obj.user in self._context['request'].user.favoriteuser.favorite_users.all()
        except:
            return False

