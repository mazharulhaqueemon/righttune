from django.utils import timezone
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
from .firebase_class import Firebase
from .functions import get_token_by_user, get_token_by_user_to_send_push_call, register_device,update_token,update_peer_user
from .push_class import Push
from accounts.models import User
from agora_token_builder import RtcTokenBuilder

# APP_ID = '10efeca3cee04cd5bdad0c2bdc09f119';
# APP_CERTIFICATE = '76f664ccd9254775b06becb9c94d8d70';
APP_ID = 'fb1751907aba4dc293a4848c708f4749'
APP_CERTIFICATE = '55086a987da64194ba54def7b0d3b9f3'


class AgoraRtcTokenRetrieveApiView(RetrieveAPIView):
    authentication_classes = []
    permission_classes = []

    def retrieve(self, request, *args, **kwargs):
        method_dict = request.GET
        channel_name = method_dict.get('channel_name',None)
        uid = method_dict.get('uid',0)
        role = method_dict.get('role',2)
        # role
        # Role_Publisher = 1: A broadcaster (host) in a live-broadcast profile. 
        # Role_Subscriber = 2: (Default) A audience in a live-broadcast profile.

        # Expire time in second
        today = timezone.now()
        privilegeExpireTs = today.timestamp() + 60*60*12 
        #Build token with uid
        rtc_token = RtcTokenBuilder.buildTokenWithUid(APP_ID, APP_CERTIFICATE, channel_name, uid, role, privilegeExpireTs)
        return Response({'rtcToken':rtc_token},status=HTTP_200_OK)

class RegisterDeviceCreateApiView(CreateAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        data_obj = request.data

        token = data_obj.get('token',None)
        user = request.user

        result = register_device(user,token)
        response = {
            'error': True,
            'response': 'Invalid Request...',
        }
        if result == 0:
            response['error'] = False
            response['message'] = 'Device registered successfully'
        elif result == 2:
            response['error'] = True
            response['message'] = 'Device already registered'
        else:
            response['error'] = True
            response['message'] = 'Device not registered'

        return Response(response,status=HTTP_201_CREATED)

class UserTokenUpdateApiView(UpdateAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        data_obj = request.data

        user = request.user
        token = data_obj.get('token',None)

        result = update_token(user,token)

        return Response({'response':result},status=HTTP_200_OK)

class PeerDeviceUpdateApiView(UpdateAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        data_obj = request.data

        user = request.user
        peer_user_id = data_obj.get('peer_user_id',None)
        
        peer_user = User.objects.filter(id=peer_user_id).first()
        if peer_user is None:
            return Response(status=HTTP_204_NO_CONTENT)

        result = update_peer_user(user,peer_user) 

        return Response({'response':result},status=HTTP_200_OK)

class SinglePushCreateApiView(CreateAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        data_obj = request.data

        title = data_obj.get('title',None)
        message = data_obj.get('message',None)
        receiver_uid = data_obj.get('receiver_uid',None)
        user = request.user
        image = data_obj.get('image',None)

        if title is not None and message is not None and receiver_uid is not None:
            receiver_user = User.objects.filter(id=receiver_uid).first()
            if receiver_user is None:
                return Response(status=HTTP_204_NO_CONTENT)
            # title, message, image, peeredUid, peeredName, callType
            push_obj = None
            if image is not None:
                push_obj = Push(title,message,image,None,None,None)
            else:
                push_obj = Push(title,message,None,None,None,None)

            push_notification_obj = push_obj.get_push()
            device_token = get_token_by_user(receiver_user,user)
            firebase_obj = Firebase()

            firebase_obj.send(device_token,push_notification_obj)

            return Response(status=HTTP_201_CREATED)

        else:
            return Response(status=HTTP_204_NO_CONTENT)

class SinglePushForCallingCreateApiView(CreateAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        data_obj = request.data
        user = request.user

        title = data_obj.get('title',None)
        message = data_obj.get('message',None)
        image = data_obj.get('image',None)
        receiver_uid = data_obj.get('receiver_uid',None)
        # Sender data
        peered_uid = user.id
        peered_name = user.profile.full_name
        call_type = data_obj.get('call_type',None)

        if title is not None and message is not None and receiver_uid is not None:
            receiver_user = User.objects.filter(id=receiver_uid).first()
            if receiver_user is None:
                return Response(status=HTTP_204_NO_CONTENT)
            # title, message, image, peeredUid, peeredName, callType
            push_obj = None
            if image is not None:
                push_obj = Push(title,message,image,peered_uid,peered_name,call_type)
            else:
                push_obj = Push(title,message,None,peered_uid,peered_name,call_type)

            push_notification_obj = push_obj.get_push()
            device_token = get_token_by_user_to_send_push_call(receiver_user)

            firebase_obj = Firebase()

            firebase_obj.send(device_token,push_notification_obj)

            return Response(status=HTTP_201_CREATED)
        else:
            return Response(status=HTTP_204_NO_CONTENT)