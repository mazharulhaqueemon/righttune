from django.conf import settings
from django.contrib import admin
from django.urls import path,include

urlpatterns = [
    # API Urls 
    path('api/v1/auth/',include("accounts.api.urls")),
    path('api/v1/balance/',include("balance.api.urls")),
    path('api/v1/call-histories/',include("call_histories.api.urls")),
    path('api/v1/favorites/',include("favorites.api.urls")),
    path('api/v1/notifications/',include("notifications.api.urls")),
    path('api/v1/profiles/',include("profiles.api.urls")),
    path('api/v1/searches/',include("searches.api.urls")),
    path('api/v1/posts/',include("post.urls")),
    path('api/v1/live-streamings/',include("livestream.urls")),


    # Firebase Cloud Messaging (FCM)
    path('api/v1/fcm/',include("fcm.api.urls")),
    
]

if settings.DEBUG:
    from django.conf.urls.static import static
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns.append(path('', admin.site.urls))