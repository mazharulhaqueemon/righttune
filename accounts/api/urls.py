from django.urls import path, include
from rest_framework import routers

from .views import (
    CreateTokenView, RegisterWithProfileCreateApiView, LogoutCreateApiView,
    ChangePasswordUpdateApiView, PasswordResetOtpCreateApiView, ResetPasswordUpdateApiView, SupportViewSet,
    AccountDeleteapi, OtpVerifyApiView,
)
router = routers.SimpleRouter()
router.register(r'Supports', SupportViewSet, basename='support')
urlpatterns=[ 
    path('token/',CreateTokenView.as_view()),
    path('register-with-profile-create/',RegisterWithProfileCreateApiView.as_view()),
    path('logout/',LogoutCreateApiView.as_view()),

    path("change-password/",ChangePasswordUpdateApiView.as_view()),
    path('password-reset-otp-create/',PasswordResetOtpCreateApiView.as_view()),
    path("reset-password/",ResetPasswordUpdateApiView.as_view()),
    path("delete/",AccountDeleteapi.as_view()),
    path("otp-verify/", OtpVerifyApiView.as_view()),
    path('', include(router.urls), name='supports'),
]