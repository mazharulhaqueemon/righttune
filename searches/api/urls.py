from django.urls import path
from .views import SearchListApiView

urlpatterns=[ 
    # ?q=search_text
    path('search/',SearchListApiView.as_view()),
]