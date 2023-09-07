from rest_framework.generics import (
    RetrieveAPIView,CreateAPIView,UpdateAPIView,
    ListAPIView, DestroyAPIView
    )
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,HTTP_203_NON_AUTHORITATIVE_INFORMATION,HTTP_204_NO_CONTENT,
    HTTP_207_MULTI_STATUS,HTTP_226_IM_USED,HTTP_208_ALREADY_REPORTED,HTTP_202_ACCEPTED,
    )
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from .serializers import FavoriteUserSerializer,UserSerializer
from favorites.models import FavoriteUser
from accounts.models import User
from notifications.models import Notification

class FavoriteUsersRetrieveApiView(RetrieveAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        user_obj = request.user
        favorite_users_obj = FavoriteUser.objects.filter(user=user_obj).first()
        if favorite_users_obj is None:
            favorite_users_obj = FavoriteUser()
            favorite_users_obj.user = user_obj
            favorite_users_obj.save()
        serializer_favorite_users = FavoriteUserSerializer(instance=favorite_users_obj,context={"request": request})
        return Response({'favorite_user_list':serializer_favorite_users.data}, status=HTTP_200_OK)

# Perform both Add and Remove user from Favorite List
class FavoriteUserCreateApiView(CreateAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        user_obj = request.user
        data_obj = request.data

        peer_uid = data_obj.get('peer_uid',0)

        peer_user_obj = User.objects.filter(id=peer_uid).first()

        if peer_user_obj is None:
            return Response({},status=HTTP_204_NO_CONTENT)

        favorite_users_obj = FavoriteUser.objects.filter(user=user_obj).first()
        notification_obj = Notification()
        notification_obj.user = peer_user_obj
        notification_obj.from_user = user_obj

        if peer_user_obj in favorite_users_obj.favorite_users.all():
            # Remove peer user from favorite list
            favorite_users_obj.favorite_users.remove(peer_user_obj) 
            notification_obj.context = 'Removes you from favorite list'
            notification_obj.save()
            return Response(status=HTTP_200_OK)
        else:
            # Add peer user to favorite list
            favorite_users_obj.favorite_users.add(peer_user_obj)
            notification_obj.context = 'Adds you into favorite list'
            notification_obj.save()
            serializer_peer_user = UserSerializer(instance=peer_user_obj,context={"request": request})

            return Response({'peer_user':serializer_peer_user.data},status=HTTP_201_CREATED)