from django.urls import path, include
from rest_framework import routers

from .views import (
    ProfileListApiView, ProfileRetrieveApiView,
    ProfileUpdateApiView, FriendViewSet, BlockUserViewSet, FollowersViewSet, IsFollowed, ProfileAsset, AssetList,
)
router = routers.SimpleRouter()
router.register(r'friends', FriendViewSet, basename='friend')
router.register(r'followers', FollowersViewSet, basename='followers')
router.register(r'block', BlockUserViewSet, basename='block')
urlpatterns=[ 
    path('profile-list/',ProfileListApiView.as_view()),
    path('profile-retrieve/<int:user_id>/',ProfileRetrieveApiView.as_view()),
    path('is_followed/<int:user_id>/',IsFollowed.as_view()),
    path('profile_assets/',ProfileAsset.as_view()),
    path('assets/',AssetList.as_view()),
    path('self-profile-update/',ProfileUpdateApiView.as_view()),
    path('', include(router.urls), name='add_friend'),
]