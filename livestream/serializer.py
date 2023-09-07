from rest_framework import serializers
from .models import ActiveCall

class ActiveCallSerializer(serializers.Serializer):
    action = serializers.CharField(required=False, allow_null=True)
    uid = serializers.CharField()
    full_name = serializers.CharField()
    profile_image = serializers.CharField()
    call_type = serializers.CharField()
    muted = serializers.BooleanField()
    video_disabled = serializers.BooleanField()
    datetime = serializers.CharField()

class ActiveCallsSerializer(serializers.Serializer):
    active_calls = ActiveCallSerializer(many=True)



    # def perform_create(self, validated_data):
    #     print("inside the create")
    #     print(validated_data)
    #     active_calls_data = validated_data.pop('active_calls')
    #     active_calls = []
    #     for call_data in active_calls_data:
    #         call = ActiveCall.objects.create(**call_data)
    #         active_calls.append(call)
    #     return active_calls
# class ActiveCallsDataSerializer(serializers.Serializer):
#     active_calls = ActiveCallsSerializer(many=True)
#
#     def create(self, validated_data):
#         active_calls_data = validated_data.pop('active_calls')
#         for call_data in active_calls_data:
#             call = ActiveCall.objects.create(**call_data)
#         return call