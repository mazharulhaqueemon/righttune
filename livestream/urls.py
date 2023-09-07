from django.urls import path
from fcm.api.views import AgoraRtcTokenRetrieveApiView
from .views import CreateActiveCallsView, liveStreamCreateApi, GiftCreate

urlpatterns = [
    path('live-streaming-state-update/', CreateActiveCallsView.as_view()),
    path('live-streaming-comment-create/',liveStreamCreateApi.as_view()),
    path('agora-rtc-token-retrieve/',AgoraRtcTokenRetrieveApiView.as_view()),
    path('live-streaming-gift-create/',GiftCreate.as_view())
]