import json

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db import transaction
from rest_framework import generics
from rest_framework.authentication import TokenAuthentication
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED,HTTP_500_INTERNAL_SERVER_ERROR

from accounts.admin import User
from post.serializer import assetSerializer
from profiles.models import Profile, UserAssets
from .serializer import ActiveCallsSerializer
from .models import ActiveCall, StreamComment, ActiveCalls, LiveStreaming


class GiftCreate(CreateAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Profile.objects.all()
    def create(self, request, *args, **kwargs):
        message = {}
        try:
            result = gift_send(from_profile=request,
                               to=User.objects.get(id=request.data['room_name']),
                               coins=request.data['gift_coins'])
            if result:
                message = {"status": "gift send successfull"}
                return Response(message,status=HTTP_201_CREATED)
            else:
                print("insdie")
                return Response(message, status=HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            print(e)
            message = {
                "error":e
            }
            return Response(message, status=HTTP_500_INTERNAL_SERVER_ERROR)


class CreateActiveCallsView(CreateAPIView):
    queryset = ActiveCall.objects.all()
    def create(self, request, *args, **kwargs):
        message = {}

        active_calls = []
        user_id = 0
        for data in request.data['active_calls']:
            user_id = data['uid']
            try:
                stream = LiveStreaming.objects.get(roomname=data['uid'])
            except LiveStreaming.DoesNotExist:
                stream = LiveStreaming.objects.create(roomname=data['uid'])
            try:
                call = ActiveCall.objects.get(uid=data['uid'])
                call.call_type = data['call_type']
                call.muted = data['muted']
                call.video_disabled = data['video_disabled']
                call.datetime = data['datetime']
                call.action = data['action']
                call.save()
            except ActiveCall.DoesNotExist:
                call = ActiveCall.objects.create(**data)

            try:
                active_call_list = ActiveCalls.objects.get(room=stream)
                active_call_list.active_calls.add(call)
            except ActiveCalls.DoesNotExist:

                active_call_list = ActiveCalls.objects.create(room=stream)
                active_call_list.active_calls.add(call)

            active_calls.append(data)
        try:

            user = User.objects.get(id=user_id)
            try:
                asset = UserAssets.objects.get(user=user)
                asset_serializer = {'name': asset.name,
                                    'level': asset.level,
                                    'image': asset.animation_image
                                    }
            except:
                asset_serializer = {}
            message = {
                'title': user.profile.full_name,
                'full_name': user.profile.full_name,
                'profile_image': str(user.profile.profile_image) if user.profile.profile_image else '',
                'active_calls': active_calls,
                'viewers': [],
                'comments': [],
                'assets': asset_serializer,
                'followers': [],
                'allow_audio_call': True,
                'allow_video_call': True,
                'pk': False,
                'earn_coins': user.profile.earn_coins,
                'earn_loves': user.profile.earn_loves,
            }
            return Response(message,status=HTTP_201_CREATED)
        except Exception as e:

            return Response(message, status=HTTP_500_INTERNAL_SERVER_ERROR)


# Create your views here.
class liveStreamCreateApi(CreateAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        user_obj = request.user
        data_obj = request.data
        StreamComment.objects.create(roomname=data_obj.get('room_name',None),text=data_obj.get('text',None),
                                      user_profile=user_obj.profile
                                      )

        return Response(status=HTTP_201_CREATED)

@transaction.atomic
def gift_send(from_profile,to,coins):
    try:
        to.profile.earn_coins += coins
        to.profile.save()
        from_profile.user.profile.earn_coins -= coins
        from_profile.user.profile.save()
        response = {}

        response['message'] = {
            'type': 'gift',
            'full_name': from_profile.user.profile.full_name,
            'profile_image': str(from_profile.user.profile.profile_image) if from_profile.user.profile.profile_image else '',
            'receiver_full_name': to.profile.full_name,
            'gift_coins': coins,
        }
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            str(to.id),
            {
                'type': 'chat_message',
                'text': json.dumps(response)
            }
        )
        response['message'] = {
            'type': 'flysms',
            'full_name': from_profile.user.profile.full_name,
            'profile_image': str(
                from_profile.user.profile.profile_image) if from_profile.user.profile.profile_image else '',
            'text': "hello",
            'receiver_full_name': to.profile.full_name,
            'gift_coins': coins,
        }
        async_to_sync(channel_layer.group_send)(
            str(to.id),
            {
                'type': 'chat_message',
                'text': json.dumps(response)
            }
        )

        return True
    except:
        return False

    return False