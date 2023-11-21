from rest_framework.generics import (
    ListAPIView, 
    )
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from .serializers import NotificationSerializer,BannerSerializer
from notifications.models import Notification,Banner

class NotificationListApiView(ListAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = NotificationSerializer

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)

class BannerListView(ListAPIView):
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]
    queryset = Banner.objects.all()
    serializer_class = BannerSerializer