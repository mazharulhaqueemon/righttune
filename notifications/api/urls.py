from django.urls import path
from .views import (
    NotificationListApiView,BannerListView
)

urlpatterns=[ 
    path('notification-list/',NotificationListApiView.as_view()),
    path('banners/', BannerListView.as_view(), name='banner-list'),
]