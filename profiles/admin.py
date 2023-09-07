from django.contrib import admin
from .models import Profile,Follow, Stories, StoryImage, UserAssets, Assets

admin.site.register(Profile)
admin.site.register(Follow)
admin.site.register(Stories)
admin.site.register(StoryImage)
admin.site.register(Assets)
admin.site.register(UserAssets)