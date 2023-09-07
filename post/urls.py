from django.urls import path
from .views import Postcreatapi, Postretriveapi, PostLikeCreateapi, PostCommentCreateapi, PostListapi, PostDeleteapi, \
    StoriesCreate, StoriesList, PostUpdateapi

urlpatterns = [
    path('newsfeed/', PostListapi.as_view()),
    path('post-create/', Postcreatapi.as_view()),
    path('post-update/<int:pk>/', PostUpdateapi.as_view()),
    path('news-feed-post-retrieve/<int:pk>/', Postretriveapi.as_view(), name='post-detail'),
    path('post-delete/<int:pk>/', PostDeleteapi.as_view(), name='Post-delete'),
    path('like-create/<int:post_id>/', PostLikeCreateapi.as_view(), name='post-like'),
    path('post-comment-create/<int:post_id>/', PostCommentCreateapi.as_view(), name='comment-list'),
    path('stories/story-create/',StoriesCreate.as_view(),name="story_create"),
    path('stories/cover-story-list/',StoriesList.as_view(),name="story_list")
]