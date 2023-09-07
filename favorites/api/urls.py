from django.urls import path
from .views import FavoriteUsersRetrieveApiView, FavoriteUserCreateApiView

urlpatterns=[ 
    path('favorite-users-retrieve/',FavoriteUsersRetrieveApiView.as_view()),
    # Perform both Add and Remove user from Favorite List
    path('favorite-user-add-or-remove/',FavoriteUserCreateApiView.as_view()),

]