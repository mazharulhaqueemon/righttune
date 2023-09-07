from django.contrib.auth import authenticate
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from accounts.models import Support


class AuthTokenSerializer(serializers.Serializer):
    phone = serializers.CharField()
    password = serializers.CharField(
        style={'input_type':'password'}
    )

    def validate(self, attrs):
        phone = attrs.get('phone')
        password = attrs.get('password')

        user = authenticate(
            request = self.context.get('request'),
            username = phone,
            password = password
        )
        if not user:
            msg = _("Unable to authenticate with provided credentials.")
            raise serializers.ValidationError(msg, code='authentication')

        attrs['user'] = user
        return attrs


class SupportSerializer(serializers.Serializer):
    text = serializers.CharField(max_length=5000)



