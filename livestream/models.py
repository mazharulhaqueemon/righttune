import json

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from accounts.admin import User
from profiles.models import Profile, UserAssets


class ActiveCall(models.Model):
    action = models.CharField(max_length=255, blank=True, null=True)
    uid = models.CharField(max_length=255,null=True)
    full_name = models.CharField(max_length=255,null=True)
    profile_image = models.CharField(max_length=255,null=True)
    call_type = models.CharField(max_length=255,null=True)
    muted = models.BooleanField()
    video_disabled = models.BooleanField()
    datetime = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.full_name} ({self.call_type})"


class LiveStreaming(models.Model):
    roomname = models.CharField(max_length=255, blank=True, null=True)
    isLive = models.BooleanField(default=True)
    isBlocked = models.BooleanField(default=False,null=True)
    priority = models.IntegerField(default=0)
    end_time = models.DateTimeField(null=True, blank=True)
    def __str__(self):
        return self.roomname
class StreamComment(models.Model):
    roomname = models.CharField(max_length=255, blank=True, null=True)
    text = models.CharField(max_length=255,null=True)
    user_profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    created_datetime = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_datetime = models.DateTimeField(auto_now=False, auto_now_add=False, blank=True, null=True)
    def __str__(self):
        return self.roomname

class ActiveCalls(models.Model):
    room = models.ForeignKey(LiveStreaming, on_delete=models.CASCADE,default=None)
    active_calls = models.ManyToManyField(ActiveCall,related_name='active_calls',blank=True,db_constraint=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.active_calls.count()} Active Calls"
# Create your models here.
# Define the signal handler
@receiver(post_save, sender=StreamComment)
def send_comments_to_websocket(sender, instance, created, **kwargs):
    if created:
        response = {}

        response['message'] = {
                'type' : 'comment',
                'userId' : instance.user_profile.id,
                'text' : instance.text,
                'full_name': instance.user_profile.full_name,
                'profile_image': str(instance.user_profile.profile_image) if instance.user_profile.profile_image else '',
                'receiver_full_name':"newuser",
                'gift_coins':10,
                'datetime' : str(instance.created_datetime)
            }
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            instance.roomname,
            {
                'type': 'chat_message',
                'text': json.dumps(response)
            }
        )


@receiver(post_save, sender=LiveStreaming)
def send_lives_to_websocket(sender, instance, created, **kwargs):
    if not created:
        channel_layer = get_channel_layer()
        response = {
            'message': []
        }
        try:
            lives = LiveStreaming.objects.filter(isLive=True, isBlocked=False).order_by('-priority', '-end_time', 'id')
            for live in lives:
                user = User.objects.get(id=live.roomname)
                list_of_calls = []
                active_call_list = ActiveCalls.objects.get(room=live)
                if active_call_list.active_calls.count() <= 0:
                    active_calls = ActiveCall.objects.create(action="broadcaster", uid=live.roomname,
                                                             full_name=user.profile.full_name,
                                                             profile_image=str(
                                                                 user.profile.profile_image) if user.profile.profile_image else '',
                                                             call_type="video", muted=True, video_disabled=False,
                                                             datetime="")
                    active_call_list.active_calls.add(active_calls)
                for calls in active_call_list.active_calls.all():
                    list_of_calls.append({
                        "action": calls.action,
                        "uid": calls.uid,
                        "full_name": calls.full_name,
                        "profile_image": str(calls.profile_image) if calls.profile_image else '',
                        "call_type": calls.call_type,
                        "muted": calls.muted,
                        "video_disabled": calls.video_disabled,
                        "datetime": calls.datetime

                    })
                try:
                    asset = UserAssets.objects.get(user=user)
                    asset_serializer = {'name': asset.name,
                                        'level': asset.level,
                                        'image': asset.animation_image
                                        }
                except:
                    asset_serializer = {}
                response['message'].append({'channelName': live.roomname,
                                            'title': user.profile.full_name,
                                            'full_name': user.profile.full_name,
                                            'profile_image': str(
                                                user.profile.profile_image) if user.profile.profile_image else '',
                                            'active_calls': list_of_calls,
                                            'viewers': [],
                                            'comments': [],
                                            'assets': asset_serializer,
                                            'followers': [],
                                            'allow_audio_call': True,
                                            'allow_video_call': True,
                                            'pk': False,
                                            'earn_coins': user.profile.earn_coins,
                                            'earn_loves': user.profile.earn_loves,
                                            })
        except Exception as e:
            print(e)
            pass

        async_to_sync(channel_layer.group_send)(
            "livestreamings",
            {
                'type': 'chat_message',
                'text': json.dumps(response)
            }
        )