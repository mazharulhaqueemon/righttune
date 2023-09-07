from django.contrib import admin
from .models import post, PostImage, PostVideo, PostLike, Comment, ImageLike, VideoLike

admin.site.register(post)
admin.site.register(PostImage)
admin.site.register(PostVideo)
admin.site.register(PostLike)
admin.site.register(ImageLike)
admin.site.register(VideoLike)
admin.site.register(Comment)
# Register your models here.
