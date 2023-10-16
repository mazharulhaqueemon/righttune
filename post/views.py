from django.shortcuts import render
from django.views.generic import UpdateView
from rest_framework.authentication import TokenAuthentication
from rest_framework.generics import CreateAPIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from profiles.models import Stories, StoryImage
from .models import post, Comment, PostImage, PostVideo, PostLike
from .serializer import CommentSerializer, ImageSerializer, VideoSerializer, postsreializer, LikeSerializer, \
    PostLikeSerializer, StorySerializer
from rest_framework import generics


class PostListapi(generics.ListAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = post.objects.all()
    serializer_class = postsreializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        message = {"posts": serializer.data}
        return Response(message)


class Postcreatapi(CreateAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, ]
    queryset = post.objects.all()
    serializer_class = postsreializer

    def create(self, request, *args, **kwargs):
        try:
            new_post = post.objects.create(text=request.data['text'], type=request.data['type'],
                                           profile=request.user.profile)

            if request.data['type'] == "text-and-image":

                for file in request.FILES.getlist('files'):
                    PostImage.objects.create(post=new_post, image=file)

            serializer = postsreializer(new_post, many=False)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except:

            return Response(status=status.HTTP_400_BAD_REQUEST)


class PostUpdateapi(CreateAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, ]
    queryset = post.objects.all()
    serializer_class = postsreializer

    def create(self, request, *args, **kwargs):
        try:
            post_id = kwargs.get('pk')
            new_post = post.objects.get(id=post_id)
            new_post.text = request.data['text']
            new_post.type = request.data['type']

            if request.data['type'] == "text-and-image":
                exist_image = PostImage.objects.filter(post=new_post)
                for img in exist_image:
                    img.image.delete()
                    img.delete()
                for file in request.FILES.getlist('files'):
                    PostImage.objects.create(post=new_post, image=file)
            new_post.save()
            serializer = postsreializer(new_post, many=False)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except:

            return Response(status=status.HTTP_400_BAD_REQUEST)


class Postretriveapi(generics.RetrieveAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = post.objects.all()
    serializer_class = postsreializer


class PostDeleteapi(generics.DestroyAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = post.objects.all()
    serializer_class = postsreializer


class PostCommentCreateapi(generics.CreateAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = post.objects.all()

    def create(self, request, *args, **kwargs):
        try:
            post_exist = post.objects.get(id=self.kwargs.get('post_id'))
            new_comment = Comment.objects.create(text=request.data['text'],
                                                 profile=request.user.profile, post=post_exist)
            serializer = CommentSerializer(new_comment, many=False)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except:

            return Response(status=status.HTTP_400_BAD_REQUEST)


class PostLikeCreateapi(generics.CreateAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = PostLike.objects.all()

    def create(self, request, *args, **kwargs):
        post_exist = post.objects.get(id=self.kwargs.get('post_id'))
        try:
            new_like = PostLike.objects.get(profile=request.user.profile, post=post_exist)
            new_like.delete()
            serializer = PostLikeSerializer(post_exist, many=True)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except:
            new_like = PostLike.objects.create(post=post_exist, profile=request.user.profile)
            serializer = PostLikeSerializer(post_exist)
            return Response(serializer.data, status=status.HTTP_201_CREATED)


class StoriesCreate(CreateAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, ]
    queryset = Stories.objects.all()

    def create(self, request, *args, **kwargs):
        try:
            new_story = Stories.objects.create(user_profile=request.user.profile, caption=request.data['caption'])

        except:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        for file in request.FILES.getlist('image'):
            StoryImage.objects.create(stories=new_story, image=file)

        message = {
            "status": "ok"
        }
        return Response(message, status=status.HTTP_201_CREATED)


class StoriesList(generics.ListAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Stories.objects.all()
    serializer_class = StorySerializer

# Create your views here.
