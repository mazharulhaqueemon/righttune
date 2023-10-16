from rest_framework import serializers

from accounts.models import User
from profiles.models import Profile, StoryImage, Stories, UserAssets, Assets
from .models import post, PostVideo, PostImage, Comment, ImageLike, PostLike as Like, VideoLike, PostLike


class PostLikeSerializer(serializers.ModelSerializer):
    likes = serializers.SerializerMethodField()

    class Meta:
        model = post
        fields = ["likes"]

    def get_likes(self, obj):
        response = []
        try:
            likes = Like.objects.filter(post=obj)
            for like in likes:
                response.append(like.profile.id)
            return response
        except:
            return response


class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ('id', 'post', 'profile', 'created_at')


class ImageSerializer(serializers.ModelSerializer):
    likes = serializers.SerializerMethodField()

    class Meta:
        model = PostImage
        fields = ('id', 'image', 'likes')

    def get_likes(self, obj):
        response = []
        likes = ImageLike.objects.filter(image=obj)
        for like in likes:
            response.append(like.profile.id)
        return response


class VideoSerializer(serializers.ModelSerializer):
    likes = serializers.SerializerMethodField()

    class Meta:
        model = PostVideo
        fields = ['id', 'video', 'video_thumbnail', 'likes']

    def get_likes(self, obj):
        response = []
        likes = VideoLike.objects.filter(video=obj)
        for like in likes:
            response.append(like.profile.id)
        return response


class UserSerializer(serializers.ModelSerializer):
    uid = serializers.IntegerField(source="id")

    class Meta:
        model = User
        fields = ['uid', 'phone']


class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(many=False)

    class Meta:
        model = Profile
        fields = "__all__"


class postsreializer(serializers.ModelSerializer):
    profile = ProfileSerializer()
    likes = serializers.SerializerMethodField()
    # likes = LikeSerializer(many=True, read_only=True)
    images = serializers.SerializerMethodField()
    video = serializers.SerializerMethodField()
    comments = serializers.SerializerMethodField()

    class Meta:
        model = post
        fields = '__all__'
        # fields = ('id', 'text', 'profile', 'created_at', 'comments', 'updated_datetime', 'images', 'video', 'likes')

    def get_likes(self, obj):
        response = []
        try:
            likes = Like.objects.filter(post=obj)
            for like in likes:
                response.append(like.profile.id)
            return response
        except:
            return response

    def get_images(self, obj):

        response = []
        try:
            query = PostImage.objects.filter(post=obj)
            images = ImageSerializer(query, many=True)
            return images.data
        except:
            return response

    def get_video(self, obj):
        response = {}
        try:
            query = PostVideo.objects.get(post=obj)
            video = VideoSerializer(query, many=False)
            return video.data
        except:

            return response

    def get_comments(self, obj):
        try:
            query = Comment.objects.filter(post=obj)
            serializer = CommentSerializer(query, many=True)
            return serializer.data
        except:
            return {}


class PostCreatesreializer(serializers.ModelSerializer):
    class Meta:
        model = post
        fields = '__all__'


class assetSerializer(serializers.ModelSerializer):
    xp = serializers.IntegerField(source='user.profile.xp')
    class Meta:
        model = UserAssets
        fields = ['id', 'level', 'xp', 'frame_store', 'vip_system']
        depth = 1


class profile_assetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assets
        fields = '__all__'


class CommentSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(many=False)

    class Meta:
        model = Comment
        fields = ('id', 'profile', 'text', 'created_datetime', 'updated_datetime')


class StoryImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = StoryImage
        fields = "__all__"


class StorySerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = Stories
        fields = "__all__"

    def get_image(self, obj):
        query = StoryImage.objects.filter(stories=obj)
        serializer = StoryImageSerializer(query, many=True)
        return serializer.data
