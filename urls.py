from django.urls import path

from fcm.api.views import AgoraRtcTokenRetrieveApiView
from livestream.views import CreateActiveCallsView

urlpatterns = [
    path('live-streaming-state-update/', CreateActiveCallsView.as_view()),
    path('agora-rtc-token-retrieve/',AgoraRtcTokenRetrieveApiView.as_view()),
]