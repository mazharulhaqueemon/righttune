from datetime import timedelta
from django.utils import timezone

from channels.consumer import AsyncConsumer
from channels.db import database_sync_to_async
import json

from accounts.models import User
from fcm.api.firebase_class import Firebase
from fcm.api.functions import get_token_by_user
from fcm.api.push_class import Push
from livestream.models import StreamComment, LiveStreaming, ActiveCall, ActiveCalls
from post.serializer import assetSerializer
from profiles.models import UserAssets


class LiveChatConsumer(AsyncConsumer):

    async def websocket_connect(self, event):
        print("connected", event)
        self.video_id = self.scope['url_route']['kwargs']['p_id']
        await self.send({
            "type": "websocket.accept",
        })
        if self.video_id != "livestreamings" and "actions" not in self.video_id and self.video_id != "live_streamings":
            await self.channel_layer.group_add(
                self.video_id,
                self.channel_name
            )
            create = await self.createStreaming()
            if create:
                await self.notify_followers()
                responselist = await self.all_live()
                await self.channel_layer.group_send(
                    "livestreamings",
                    {
                        'type': 'chat_message',
                        'text': json.dumps(responselist)
                    }
                )
            comments = await self.all_comment()
            for comment in comments:
                await self.chat_message(
                    {
                        'type': 'chat_message',
                        'text': json.dumps(comment)
                    }
                )


        elif "actions" in self.video_id:
            await self.channel_layer.group_add(
                self.video_id,
                self.channel_name
            )
        elif self.video_id == "livestreamings":
            await self.channel_layer.group_add(
                self.video_id,
                self.channel_name
            )
            responselist = await self.all_live()
            await self.chat_message(
                {
                    'type': 'chat_message',
                    'text': json.dumps(responselist)
                }
            )
        else:
            pass






    async def websocket_receive(self, event):

        front_text = event.get('text', None)

        if front_text is not None:
            loaded_dict_data = json.loads(front_text)
            goaway = loaded_dict_data.get('away',None)
            minute = loaded_dict_data.get('minute',None)
            coins = loaded_dict_data.get('coins', None)
            type = loaded_dict_data.get('type', None)
            if type == "joined":
                response = {
                    "message" : {
                        "type": "joined",
                        "userId": loaded_dict_data.get('userId', None),
                        "full_name": loaded_dict_data.get('full_name', None),
                        "profile_image": loaded_dict_data.get('profile_image', None)
                    }
                }

                await self.channel_layer.group_send(
                    self.video_id,
                    {
                        'type': 'chat_message',
                        'text': json.dumps(response)
                    }
                )
                animationImage, user_level = await self.user_animation(uid=loaded_dict_data.get('userId', None))
                response2 = {
                    "message": {
                        "action": "user_joined",
                        "uid": loaded_dict_data.get('userId', None),
                        "full_name": loaded_dict_data.get('full_name', None),
                        "profile_image": loaded_dict_data.get('profile_image', None),
                        "animation_image" : animationImage,
                        "user_level": user_level
                    }
                }

                await self.channel_layer.group_send(
                        f"{self.video_id}_actions",
                        {
                            'type': 'chat_message',
                            'text': json.dumps(response2)
                        }
                    )
            if type == "flysms":
                await self.fly_sms_coins_minus(uid=loaded_dict_data.get('uid', None))
                response = {
                    "message": {
                        "type": 'flysms',
                        'uid': loaded_dict_data.get('uid', None),
                        "full_name": loaded_dict_data.get('full_name', None),
                        "profile_image": loaded_dict_data.get('profile_image', None),
                        "text": loaded_dict_data.get('text', None)
                    }
                }

                await self.channel_layer.group_send(
                    self.video_id,
                    {
                        'type': 'chat_message',
                        'text': json.dumps(response)
                    }
                )
            if type == "love":

                response = {
                        "message": {
                            "type": 'love',
                            'uid': loaded_dict_data.get('uid', None),
                            "full_name": loaded_dict_data.get('full_name', None),
                            "profile_image": loaded_dict_data.get('profile_image', None),
                            "text": loaded_dict_data.get('text', None)
                        }
                    }
                await self.love_coins_add(uid=self.video_id,loves=loaded_dict_data.get('love_count', None))
                await self.channel_layer.group_send(
                        self.video_id,
                        {
                            'type': 'chat_message',
                            'text': json.dumps(response)
                        }
                    )
            if "actions" in self.video_id:
                action = loaded_dict_data['message'].get('action', None)
                room_name = loaded_dict_data['message'].get('room_name', None)
                uid = loaded_dict_data['message'].get('uid', None)
                full_name = loaded_dict_data['message'].get('full_name', None)
                profile_image = loaded_dict_data['message'].get('profile_image', None)
                call_type = loaded_dict_data['message'].get('call_type', None)
                muted = loaded_dict_data['message'].get('muted', None)
                video_disabled = loaded_dict_data['message'].get('video_disabled', None)
                if action == "call_request" or action == "cancel_request" or action == "end_call" or action == "active_users" or action == "controller" or action == "pk_request" or action == "cancel_pk_request" or action == "end_pk_call" or action == "controller_pk" or action == "active_pk_list":

                    response = {
                            "message": {
                                "room_name": room_name,
                                "action": action,
                                "uid": uid,
                                "full_name": full_name,
                                "profile_image": profile_image,
                                "call_type": call_type,
                                "muted": muted,
                                "video_disabled": video_disabled
                            }
                        }
                    await self.channel_layer.group_send(
                        room_name,
                        {
                            'type': 'chat_message',
                            'text': json.dumps(response)
                        }
                    )
                    await self.save_active_calls(action, uid, full_name, profile_image, call_type, muted,
                                                 video_disabled)
                elif action == "end_active_pks" or action == "end_active_calls":
                    response = {
                        "message": {
                            "room_name": room_name,
                            "action": action,
                        }
                    }
                    await self.channel_layer.group_send(
                        room_name,
                        {
                            'type': 'chat_message',
                            'text': json.dumps(response)
                        }
                    )
                elif action == "user_offline":
                    response = {
                        "message": {
                            "action": action,
                            "uid": uid,
                        }
                    }
                    await self.channel_layer.group_send(
                        room_name,
                        {
                            'type': 'chat_message',
                            'text': json.dumps(response)
                        }
                    )

                responselist = await self.all_live()
                await self.channel_layer.group_send(
                        "livestreamings",
                        {
                            'type': 'chat_message',
                            'text': json.dumps(responselist)
                        }
                    )



            if minute is not None:
                await self.rocket_api(minute=minute,coins=coins)
            if goaway is not None:
                await self.awayStreaming()
                responselist = await self.all_live()
                await self.channel_layer.group_send(
                    "livestreamings",
                    {
                        'type': 'chat_message',
                        'text': json.dumps(responselist)
                    }
                )




    async def websocket_disconnect(self, event):
        await self.channel_layer.group_discard(
            self.video_id,
            self.channel_name
        )

        print("disconnected", event)


    @database_sync_to_async
    def all_comment(self):

        response = [

        ]
        try:
            comments = StreamComment.objects.filter(roomname=self.video_id)
        except:
            return response


        for comment in comments:

            response.append({
                'message':{
                'type' : 'comment',
                'userId' : comment.user_profile.id,
                'text' : comment.text,
                'full_name': comment.user_profile.full_name,
                'profile_image': str(comment.user_profile.profile_image) if comment.user_profile.profile_image else '',
                'receiver_full_name':"newuser",
                'gift_coins':10,
                'datetime' : str(comment.created_datetime)
                }
            }
            )
        return response


    @database_sync_to_async
    def delete(self):
        StreamComment.objects.filter(roomname=self.video_id).delete()
    async def chat_message(self, event):
        await self.send({
            "type": "websocket.send",
            "text": event['text'],

        })

    @database_sync_to_async
    def createStreaming(self):
        try:
            live = LiveStreaming.objects.get(roomname=self.video_id)
            if live.isLive:
                return False
            else:
                live.isLive=True
                live.save()
                return True
        except:
            new_stream = LiveStreaming.objects.create(roomname=self.video_id)
            ActiveCalls.objects.create(room=new_stream)
            return True

    @database_sync_to_async
    def awayStreaming(self):

        try:
            live = LiveStreaming.objects.get(roomname=self.video_id)
            try:
                comments = StreamComment.objects.filter(roomname=self.video_id)
                for comment in comments:
                    comment.delete()
                call = ActiveCall.objects.get(uid=self.video_id)
                call.delete()
            except:
                pass
            live.delete()
        except:
            pass
    @database_sync_to_async
    def all_live(self):

        response = {
            'message': []
        }
        try:
            lives = LiveStreaming.objects.filter(isLive=True,isBlocked=False).order_by('-priority', '-end_time','id')
            for live in lives:
                user = User.objects.get(id=live.roomname)
                list_of_calls = []
                active_call_list = ActiveCalls.objects.get(room=live)
                try:
                    active_calls = ActiveCall.objects.get(uid=user.id)
                except ActiveCall.DoesNotExist:
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
                    print(asset)
                    asset_serializer = {'name':asset.name,
                                        'level':asset.level,
                                        'image':asset.animation_image
                                        }
                except Exception as e:
                    print(e)
                    asset_serializer = {}
                response['message'].append({'channelName':live.roomname,
                            'title': user.profile.full_name,
                                'full_name': user.profile.full_name,
                                'profile_image':  str(user.profile.profile_image) if user.profile.profile_image else '',
                                'active_calls': list_of_calls,
                                'viewers': [],
                                'comments': [],
                                'assets': asset_serializer,
                                'followers': [],
                                'allow_audio_call': True,
                                'allow_video_call': True,
                                'pk': False,
                                'earn_coins':user.profile.earn_coins,
                                'earn_loves': user.profile.earn_loves,
                                })

        except :

            pass;
        return response

    @database_sync_to_async
    def notify_followers(self):
        try:
            user = User.objects.get(id=self.video_id)
            followers = user.profile.followers.all()
            title = "New Live"
            message = f"{user.profile.full_name} is live now"
            for follower in followers:
                if title is not None and message is not None:
                    # title, message, image, peeredUid, peeredName, callType
                    push_obj = Push(title, message, None, None, None, None)
                    push_notification_obj = push_obj.get_push()
                    device_token = get_token_by_user(follower, user)
                    firebase_obj = Firebase()
                    firebase_obj.send(device_token, push_notification_obj)
        except:
            pass

    @database_sync_to_async
    def rocket_api(self,minute,coins):
        try:
            stream = LiveStreaming.objects.get(roomname=self.video_id, isLive=True)
            stream.priority = 1
            stream.end_time = timezone.now() + timedelta(
                minutes=minute)  # Add the duration based on coins spent
            stream.save()
            user_profile = User.objects.get(id=self.video_id)
            user_profile.profile.earn_coins -= coins
            user_profile.profile.save()

        except Exception as e:
            print(e)
            pass

    @database_sync_to_async
    def save_active_calls(self, action, uid, full_name, profile_image, call_type, muted, video_disabled):
        try:
            stream = LiveStreaming.objects.get(roomname=self.video_id[0], isLive=True)
            calls = ActiveCalls.objects.get(room=stream)
            try:
                call = ActiveCall.objects.get(uid=uid)
                call.call_type = call_type
                call.muted = muted
                call.video_disabled = video_disabled
                call.action = action
                call.save()
            except ActiveCall.DoesNotExist:
                call = ActiveCall.objects.create(action=action,uid=uid, full_name=full_name,
                                                             profile_image=profile_image,
                                                             call_type=call_type, muted=muted, video_disabled=video_disabled, datetime="")
            calls.active_calls.add(call)

        except Exception as e:
            print(e)
            pass

    @database_sync_to_async
    def fly_sms_coins_minus(self, uid):

        try:
            user = User.objects.get(id=uid)
            if user.profile.earn_coins >= 2:
                user.profile.earn_coins -= 2
                user.profile.save()
        except:
            pass

    @database_sync_to_async
    def user_animation(self, uid):

        try:
            user = User.objects.get(id=uid)
            user_asset = UserAssets.objects.get(user=user)
            return user_asset.animation_image, user_asset.level
        except:
            return "", ""

    @database_sync_to_async
    def love_coins_add(self, uid, loves):

        try:
            user = User.objects.get(id=uid)
            user.profile.earn_loves += loves
            user.profile.save()
        except:
            pass
