from rest_framework import serializers
from balance.models import (
    PaymentMethod,DepositRequest,WithdrawRequest,Balance,
    Plan,PlanPurchased,EarningHistory
    )

class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = '__all__'

class PlanPurchasedSerializer(serializers.ModelSerializer):
    plan = serializers.SerializerMethodField()
   
    class Meta:
        model = PlanPurchased
        fields = ['id','user','plan','minutes','expired_datetime']

    def get_plan(self,obj):
        plan_obj = obj.plan
        return PlanSerializer(instance=plan_obj,context={"request": self._context['request']}).data

class PaymentMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentMethod
        fields = '__all__'

class DepositRequestSerializer(serializers.ModelSerializer):
    payment_method = serializers.SerializerMethodField()
   
    class Meta:
        model = DepositRequest
        fields = ['id','payment_method','screenshot','amount','sender_number','transaction_id','feedback','is_pending','is_accepted','is_declined','requested_datetime']

    def get_payment_method(self,obj):
        payment_method_obj = obj.payment_method
        return PaymentMethodSerializer(instance=payment_method_obj,context={"request": self._context['request']}).data

class WithdrawRequestSerializer(serializers.ModelSerializer):
    payment_method = serializers.SerializerMethodField()
    
    class Meta:
        model = WithdrawRequest
        fields = ['id','payment_method','amount','received_amount','receiver_number','feedback','is_pending','is_accepted','is_declined','requested_datetime']

    def get_payment_method(self,obj):
        payment_method_obj = obj.payment_method
        return PaymentMethodSerializer(instance=payment_method_obj,context={"request": self._context['request']}).data


class BalanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Balance
        fields = '__all__'

class EarningHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = EarningHistory
        fields = '__all__'
