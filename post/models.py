import uuid
import os
from django.db import models

from metazo.utils import delete_file
from profiles.models import Profile


class post(models.Model):
    text = models.CharField(max_length=200)
    type = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_datetime = models.DateTimeField(auto_now=False, auto_now_add=False, blank=True, null=True)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)


def post_image(instance, filename):
    ext = filename.split('.')[-1]
    filename = f'{uuid.uuid4()}.{ext}'

    return os.path.join('profiles/post_image/', filename)


def post_video(instance, filename):
    ext = filename.split('.')[-1]
    filename = f'{uuid.uuid4()}.{ext}'

    return os.path.join('profiles/post_video/', filename)


def post_thumbnail(instance, filename):
    ext = filename.split('.')[-1]
    filename = f'{uuid.uuid4()}.{ext}'

    return os.path.join('profiles/post_thumbnail/', filename)


class PostLike(models.Model):
    post = models.ForeignKey(post, on_delete=models.CASCADE, related_name='post_like_post', null=True)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)


class PostImage(models.Model):
    post = models.ForeignKey(post, on_delete=models.CASCADE, related_name='post_image_post', null=True)
    image = models.ImageField(upload_to=post_image, blank=True, null=True)

    def delete(self, *args, **kwargs):
        if self.image:
            delete_file(self.image.path)

        super().delete(*args, **kwargs)


class PostVideo(models.Model):
    post = models.ForeignKey(post, on_delete=models.CASCADE, null=True)
    video = models.FileField(upload_to=post_video, blank=True, null=True)
    video_thumbnail = models.ImageField(upload_to=post_thumbnail, blank=True, null=True)
    # hls_url = models.URLField(default='http://127.0.0.1:8000/hls/playlist.m3u8')
    # hls_path = models.FilePathField(path='profiles/post_video/hls')
    # hls_keys_path = models.FilePathField(path='profiles/post_video/keys')
    # hls_url = models.URLField()
    # hls_path = models.FilePathField()
    # hls_keys_path = models.FilePathField()

    def delete(self, *args, **kwargs):
        if self.video:
            delete_file(self.video.path)
        if self.video_thumbnail:
            delete_file(self.video_thumbnail.path)

        super().delete(*args, **kwargs)


class ImageLike(models.Model):
    image = models.ForeignKey(PostImage, on_delete=models.CASCADE, related_name='post_image_like_post', null=True)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)


class VideoLike(models.Model):
    video = models.ForeignKey(PostVideo, on_delete=models.CASCADE, null=True)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)


class Comment(models.Model):
    post = models.ForeignKey(post, on_delete=models.CASCADE, related_name='comments')
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    text = models.TextField()
    created_datetime = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_datetime = models.DateTimeField(auto_now=False, auto_now_add=False, blank=True, null=True)


class xyz(models.Model):
    text = models.CharField(max_length=200)
    type = models.CharField(max_length=200)
