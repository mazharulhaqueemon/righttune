from django.utils import timezone
from datetime import date

from rest_framework import viewsets, status
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

from accounts.models import User
from fcm.api.firebase_class import Firebase
from fcm.api.functions import get_token_by_user
from fcm.api.push_class import Push
from post.serializer import assetSerializer, profile_assetSerializer
from profiles.models import Profile, UserAssets, Assets,FrameStore,BalanceHistory
from .serializers import ProfileSerializer, ProfileDetailsSerializer, ProfileDetailsOfOtherUserSerializer, \
    FriendSerializer, FriendListSerializer, FriendListProfileSerializer, FollowerSerializer,FrameStoreSerializer,BalanceHistorySerializer
from searches.api.serializers import SearchSerializer
from metazo.utils import compress,delete_file

class ProfileListApiView(ListAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        profile_objs = Profile.objects.exclude(user=request.user)

        serializer_profile = ProfileSerializer(instance=profile_objs,many=True,context={"request": request})

        return Response({'profiles':serializer_profile.data},status=HTTP_200_OK)


class ProfileRetrieveApiView(RetrieveAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    lookup_field = 'user_id'

    def retrieve(self, request, *args, **kwargs):
        user = request.user
        user_id = self.kwargs[self.lookup_field]
        profile_obj = None
        if user_id == user.id:
            # My Profile
            profile_obj = user.profile
            serializer_profile = ProfileSerializer(instance=profile_obj,context={"request": request})
        else:
            # Other Profile
            profile_obj = Profile.objects.filter(user__id=user_id).first()
            serializer_profile = ProfileSerializer(instance=profile_obj,context={"request": request})

        if profile_obj is None:
            return Response(status=HTTP_204_NO_CONTENT)
        return Response({'profile':serializer_profile.data}, status=HTTP_200_OK)

class ProfileUpdateApiView(UpdateAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        data_obj = request.data
        user = request.user
        full_name = data_obj.get('full_name',None)
        profile_image = data_obj.get('profile_image',None)
        # cover_image = data_obj.get('cover_image',None)
        birthday = data_obj.get('birthday',None) 
        gender = data_obj.get('gender',None)
        address = data_obj.get('address',None)
        about = data_obj.get('about',None)

        profile_obj = user.profile

        if profile_image:
            if profile_obj.profile_image:
                delete_file(profile_obj.profile_image.path)
            compressed_image = compress(profile_image)
            # Choosing smaller image size
            if compressed_image.size > profile_image.size:
                compressed_image = profile_image
            profile_obj.profile_image = compressed_image

        # if cover_image:
        #     if profile_obj.cover_image:
        #         delete_file(profile_obj.cover_image.path)
        #     compressed_image = compress(cover_image)
        #     # Choosing smaller image size
        #     if compressed_image.size > cover_image.size:
        #         compressed_image = cover_image
        #     profile_obj.cover_image = compressed_image

        if full_name:
            profile_obj.full_name = full_name
        if gender:
            profile_obj.gender = gender
        if address:
            profile_obj.address = address
        if about:
            profile_obj.about = about

        if birthday:
            # 2014-08-14T00:00:00.000
            birthday = birthday.split('T')[0]
            birthday_list = birthday.split('-')
            birthday = date(int(birthday_list[0]),int(birthday_list[1]),int(birthday_list[2]))
            profile_obj.birthday = birthday

        profile_obj.updated_date = timezone.now().date()
        profile_obj.save()

        serializer_profile = ProfileSerializer(instance=profile_obj,context={"request": request})
        return Response({'profile':serializer_profile.data}, status=HTTP_200_OK)



class FriendViewSet(viewsets.ViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    def create(self, request):
        serializer = FriendSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['phone']
            try:
                friend_user = User.objects.get(phone=username)
                friend_profile = Profile.objects.get(user=friend_user)
                my_profile = Profile.objects.get(user=request.user)
                my_profile.friends.add(friend_user)
                friend_profile.friends.add(request.user)
                return Response(status=status.HTTP_200_OK)
            except User.DoesNotExist:
                return Response({'error': 'User does not exist'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def list(self, request):
        my_profile = Profile.objects.get(user=request.user)
        friends = my_profile.friends.all()
        profiles = [friend_profile.profile for friend_profile in friends]
        serializer = FriendListProfileSerializer(profiles, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

class FollowersViewSet(viewsets.ViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    def create(self, request):
        serializer = FollowerSerializer(data=request.data)
        if serializer.is_valid():
            uid = serializer.validated_data['uid']
            try:
                friend_user = User.objects.get(id=uid)
                friend_profile = Profile.objects.get(user=friend_user)
                my_profile = Profile.objects.get(user=request.user)
                friend_profile.followers.add(request.user)

                title = "New Follower"
                message = f"{my_profile.full_name} followed you"
                image = None
                if title is not None and message is not None:
                    if friend_user is None:
                        return Response(status=HTTP_204_NO_CONTENT)
                    # title, message, image, peeredUid, peeredName, callType
                    push_obj = Push(title, message, None, None, None, None)
                    push_notification_obj = push_obj.get_push()
                    device_token = get_token_by_user(friend_user, request.user)
                    firebase_obj = Firebase()
                    firebase_obj.send(device_token, push_notification_obj)
                return Response(status=status.HTTP_200_OK)
            except User.DoesNotExist:
                return Response({'error': 'User does not exist'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request,pk=None):
        # Get the current user's profile

        try:
            # Get the user to block by their username
            user_to_unfollow = User.objects.get(id=pk)
            # Add the other user to the current user's blocked list
            user_to_unfollow.profile.followers.remove(request.user)

            return Response({'status': 'success'}, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            # Return an error response if the user to block does not exist
            return Response({'error': 'User does not exist'}, status=status.HTTP_404_NOT_FOUND)

    def list(self, request):
        my_profile = Profile.objects.get(user=request.user)
        friends = my_profile.followers.all()
        profiles = [friend_profile.profile for friend_profile in friends]
        serializer = FriendListProfileSerializer(profiles, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

class IsFollowed(RetrieveAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    lookup_field = 'user_id'

    def retrieve(self, request, *args, **kwargs):
        user = request.user
        user_id = self.kwargs[self.lookup_field]
        try:
            follower = User.objects.get(id=user_id)
            if follower in user.profile.followers.all():
                return Response({"result":True},status=HTTP_200_OK)
            else:
                return Response({"result": False}, status=HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"result": False}, status=HTTP_200_OK)

class ProfileAsset(CreateAPIView):
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]
    queryset = UserAssets.objects.all()

    def create(self, request, *args, **kwargs):
        try:
            asset = UserAssets.objects.get(user=request.user)
            asset.name = request.data['name']
            asset.level = request.data['level']
            asset.animation_image = request.data['image']
            asset.save()
            request.user.profile.earn_coins -= int(request.data['price'])
            request.user.profile.save()
            serializer = assetSerializer(asset, many=False)

            return Response(serializer.data, status=status.HTTP_200_OK)

        except UserAssets.DoesNotExist:
            asset = UserAssets.objects.create(user=request.user,name=request.data['name'], level=request.data['level'],animation_image = request.data['image'])


            request.user.profile.earn_coins -= int(request.data['price'])
            request.user.profile.save()
            serializer = assetSerializer(asset, many=False)

            return Response(serializer.data, status=status.HTTP_200_OK)

##### Frame asset by Emon

class FrameAsset(CreateAPIView):
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]
    queryset = UserAssets.objects.all()

    def create(self, request, *args, **kwargs):
        try:
            asset = UserAssets.objects.get(user=request.user)

        except UserAssets.DoesNotExist:
            asset = UserAssets.objects.create(user=request.user)

        frame_id = request.data['id']
        frame = FrameStore.objects.get(id=frame_id)
        if request.user.balance.amount < int(frame.price):
            return Response({'error': 'You do not have enough coins'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            asset.frame_store = frame
            asset.save()
            request.user.balance.amount -= int(frame.price)
            request.user.balance.save()
            BalanceHistory.objects.create(user=request.user, info=f"Buy frame {frame.title}",
                                          amount=frame.price)
        serializer = assetSerializer(asset, many=False)

        return Response(serializer.data, status=status.HTTP_200_OK)



class AssetList(ListAPIView):
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        asset_list = Assets.objects.all()

        serializer_assets = profile_assetSerializer(instance=asset_list,many=True)

        return Response(serializer_assets.data,status=HTTP_200_OK)
class BlockUserViewSet(viewsets.ViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    def create(self, request):
        # Get the current user's profile
        my_profile = Profile.objects.get(user=request.user)

        # Get the username of the user to block
        uid = request.data.get('uid')

        try:
            # Get the user to block by their username
            user_to_block = User.objects.get(id=uid)

            # Get the profile of the user to block
            profile_to_block = user_to_block.profile

            # Remove the user from the current user's friends list
            my_profile.friends.remove(user_to_block)
            my_profile.followers.remove(user_to_block)

            # Remove the current user from the other user's friends list
            profile_to_block.friends.remove(request.user)
            profile_to_block.followers.remove(request.user)

            # Add the other user to the current user's blocked list
            my_profile.blocked_users.add(user_to_block)

            return Response({'status': 'success'}, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            # Return an error response if the user to block does not exist
            return Response({'error': 'User does not exist'}, status=status.HTTP_404_NOT_FOUND)

    def update(self, request,pk=None):
        # Get the current user's profile
        my_profile = Profile.objects.get(user=request.user)

        try:
            # Get the user to block by their username
            user_to_block = User.objects.get(id=pk)
            # Add the other user to the current user's blocked list
            my_profile.blocked_users.remove(user_to_block)

            return Response({'status': 'success'}, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            # Return an error response if the user to block does not exist
            return Response({'error': 'User does not exist'}, status=status.HTTP_404_NOT_FOUND)

    def list(self, request):
        my_profile = Profile.objects.get(user=request.user)
        blockeds = my_profile.blocked_users.all()
        profiles = [block_profile.profile for block_profile in blockeds]
        serializer = FriendListProfileSerializer(profiles, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

class FrameStoreListView(ListAPIView):
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]
    queryset = FrameStore.objects.all()
    serializer_class = FrameStoreSerializer

class UserAssetListView(ListAPIView):
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]
    serializer_class = assetSerializer

    def get_queryset(self):
        return UserAssets.objects.exclude(frame_store=None)

class BalanceHistoryListAPIView(ListAPIView):
    serializer_class = BalanceHistorySerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
