from django.urls import path
from .views import (
    NotificationListApiView
)

urlpatterns=[ 
    path('notification-list/',NotificationListApiView.as_view()),
]