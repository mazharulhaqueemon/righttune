from decimal import Decimal
from django.utils import timezone
from datetime import date
from datetime import timedelta

from rest_framework.generics import (
    RetrieveAPIView,CreateAPIView,UpdateAPIView,
    ListAPIView, DestroyAPIView,
    )
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_202_ACCEPTED,
    HTTP_203_NON_AUTHORITATIVE_INFORMATION,
    HTTP_204_NO_CONTENT,
    HTTP_205_RESET_CONTENT,
    HTTP_206_PARTIAL_CONTENT,
    HTTP_207_MULTI_STATUS,
    HTTP_208_ALREADY_REPORTED,
    HTTP_226_IM_USED, 
    )
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from accounts.models import User
from balance.models import (
    PaymentMethod, DepositRequest, WithdrawRequest, Balance,
    Plan, PlanPurchased, EarnMinuteExchanger, EarningHistory, EarnCoinExchanger,
)
from .serializers import (
    PaymentMethodSerializer,DepositRequestSerializer,WithdrawRequestSerializer,BalanceSerializer,
    PlanSerializer,PlanPurchasedSerializer,EarningHistorySerializer,
    )
from metazo.utils import compress

class PlanListApiView(ListAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = PlanSerializer
    queryset = Plan.objects.all()

class PlanPurchasedListApiView(ListAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = PlanPurchasedSerializer
    
    def get_queryset(self):
        present_datetime = timezone.now()
        return PlanPurchased.objects.filter(user=self.request.user,expired_datetime__gte=present_datetime)

class PlanPurchasedRemaingMinutesRetrieveApiView(RetrieveAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        present_datetime = timezone.now()
        has_minutes = False
        # 5 seconds = .08333333 ~ minutes
        plan_purchased_objs = PlanPurchased.objects.filter(user=request.user,expired_datetime__gte=present_datetime,minutes__gt=5/60) # 5 seconds = .08333333 ~ minute
        if plan_purchased_objs:
            has_minutes = True
        return Response({'allowed_call':has_minutes,},status=HTTP_200_OK)

class DashboardRetrieveApiView(RetrieveAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        present_datetime = timezone.now()
        total_earning = Decimal(0.0)
        remaining_minutes = Decimal(0.0)
        plan_purchased_objs = PlanPurchased.objects.filter(user=request.user,expired_datetime__gte=present_datetime) 
        if plan_purchased_objs:
            for plan_purchased_obj in plan_purchased_objs:
                remaining_minutes += plan_purchased_obj.minutes

        balance_obj = Balance.objects.filter(user=request.user).first()
        if balance_obj:
            total_earning = balance_obj.earn_amount
        return Response({'total_earning':total_earning,'remaining_minutes':remaining_minutes,},status=HTTP_200_OK)

class WalletRetrieveApiView(RetrieveAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        present_datetime = timezone.now()
        total_earning = Decimal(0.0)
        balance_obj = Balance.objects.filter(user=request.user).first()
        if balance_obj:
            total_earning = balance_obj.earn_amount

        earning_history_objs = EarningHistory.objects.filter(user=request.user).order_by('-date')
        serializer_earning_histories = EarningHistorySerializer(instance=earning_history_objs,many=True,context={'request': request})
        return Response({'total_earning':total_earning,'earning_histories':serializer_earning_histories.data,},status=HTTP_200_OK)

class PlanPurchasedCreateApiView(CreateAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        data_obj = request.data
        user = request.user

        plan_id = data_obj.get('plan_id',None)
        if plan_id:
            plan_obj = Plan.objects.filter(id=plan_id).first()
            if plan_obj:
                balance_obj = Balance.objects.filter(user=user).first()
                # No sufficient amount to purchase plan
                if balance_obj is None or balance_obj.amount < plan_obj.price:
                    return Response(status=HTTP_203_NON_AUTHORITATIVE_INFORMATION)

                # Paid for Plan
                balance_obj.amount -= plan_obj.price
                balance_obj.save()
                plan_purchased_obj = PlanPurchased.objects.filter(user=user,plan=plan_obj).first()
                if plan_purchased_obj:
                    # Update
                    expired_datetime = timezone.now() + timedelta(days=plan_obj.days)
                    if plan_purchased_obj.expired_datetime >= timezone.now():
                        # Added with provious minutes
                        plan_purchased_obj.minutes += Decimal(float(plan_obj.minutes))
                    else:
                        # Don't add with privous minutes because of expiration
                        plan_purchased_obj.minutes = Decimal(float(plan_obj.minutes))
                    plan_purchased_obj.expired_datetime = expired_datetime
                    plan_purchased_obj.save()
                else:
                    # Create
                    expired_datetime = timezone.now() + timedelta(days=plan_obj.days)
                    plan_purchased_obj = PlanPurchased()
                    plan_purchased_obj.user = user
                    plan_purchased_obj.plan = plan_obj
                    plan_purchased_obj.minutes = Decimal(float(plan_obj.minutes))
                    plan_purchased_obj.expired_datetime = expired_datetime
                    plan_purchased_obj.save()
                serializer_plan_purchased = PlanPurchasedSerializer(instance=plan_purchased_obj,context={'request': request})
                return Response({'purchased_plan':serializer_plan_purchased.data,},status=HTTP_201_CREATED)

        return Response(status=HTTP_204_NO_CONTENT)

class PaidForCallCreateApiView(CreateAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        data_obj = request.data
        user = request.user

        call_type = data_obj.get('call_type',None)
        seconds = data_obj.get('seconds',None)
        receiver_uid = data_obj.get('receiver_uid',None)        
       
        if receiver_uid:
            peer_user_obj = User.objects.filter(id=receiver_uid).first()
            if peer_user_obj and seconds > 0:
                present_datetime = timezone.now()
                # 5 seconds = .08333333 ~ minutes
                plan_purchased_objs = PlanPurchased.objects.filter(user=self.request.user,expired_datetime__gte=present_datetime,minutes__gt=5/60).order_by('expired_datetime') # 5 seconds = .08333333 ~ minutes
                if plan_purchased_objs is None:
                    return Response(status=HTTP_204_NO_CONTENT)

                plan_purchased_obj = plan_purchased_objs.first()
                plan_purchased_obj.minutes -= Decimal(seconds/60)
                plan_purchased_obj.save()

                earn_minute_exchanger_obj = EarnMinuteExchanger.objects.last()
                if earn_minute_exchanger_obj is None:
                    earn_minute_exchanger_obj = EarnMinuteExchanger()
                    earn_minute_exchanger_obj.per_minute_rate = Decimal(.20)
                    earn_minute_exchanger_obj.save()

                earm_amount = Decimal(seconds/60) * earn_minute_exchanger_obj.per_minute_rate
                balance_obj = Balance.objects.filter(user=peer_user_obj).first()
                if balance_obj is None:
                    # Create earn amount
                    balance_obj = Balance()
                    balance_obj.user = peer_user_obj
                    balance_obj.earn_amount = Decimal(earm_amount)
                    balance_obj.updated_datetime = timezone.now()
                    balance_obj.save()
                else:
                    # Update earn amount
                    balance_obj.earn_amount += Decimal(earm_amount)
                    balance_obj.updated_datetime = timezone.now()
                    balance_obj.save()

                datetime_now = timezone.now()
                today_date = date(datetime_now.year,datetime_now.month,datetime_now.day)
                earning_history_obj = EarningHistory.objects.filter(user=peer_user_obj,date=today_date).first()
                if earning_history_obj is None:
                    # Create
                    earning_history_obj = EarningHistory()
                    earning_history_obj.user = peer_user_obj
                    earning_history_obj.earn_amount = Decimal(earm_amount)
                    earning_history_obj.save()
                else:
                    # Update
                    earning_history_obj.earn_amount += Decimal(earm_amount)
                    earning_history_obj.save()

                return Response(status=HTTP_201_CREATED)

        return Response(status=HTTP_204_NO_CONTENT)

class PaymentMethodListApiView(ListAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = PaymentMethodSerializer

    def list(self, request, *args, **kwargs):
        user = request.user
        payment_methods_objs = PaymentMethod.objects.all()
        serializer_payment_methods = PaymentMethodSerializer(instance=payment_methods_objs,many=True,context={'request': request})

        return Response({'payment_methods':serializer_payment_methods.data,},status=HTTP_200_OK)
    
# class BalanceRetrieveApiView(RetrieveAPIView):
#     authentication_classes = [TokenAuthentication]
#     permission_classes = [IsAuthenticated]
#
#     def retrieve(self, request, *args, **kwargs):
#         balance_obj = Balance.objects.filter(user=request.user).first()
#         serializer_balance = BalanceSerializer(instance=balance_obj,context={'request': request})
#         return Response({'balance':serializer_balance.data,},status=HTTP_200_OK)

class BalanceRetrieveApiView(RetrieveAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        rate = EarnCoinExchanger.objects.all().first()
        data = {
            "balance": {
                "earncoins":request.user.profile.earn_coins
            },
            "earn_coin_exchanger":{
                "per_coin_rate": rate.per_coin_rate
            }
        }
        return Response(data, status=HTTP_200_OK)

class DepositRequestListApiView(ListAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        user = request.user
        deposit_request_objs = DepositRequest.objects.filter(user=user)
        serializer_deposit_request_list = DepositRequestSerializer(instance=deposit_request_objs,many=True,context={'request': request})

        return Response({'deposit_request_list':serializer_deposit_request_list.data,},status=HTTP_200_OK)

class DepositRequestCreateApiView(CreateAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        data_obj = request.data
        user = request.user

        payment_method_id = data_obj.get('payment_method',None)
        amount = data_obj.get('amount',None)
        screenshot = data_obj.get('screenshot',None)
        sender_number = data_obj.get('sender_number',None)
        transaction_id = data_obj.get('transaction_id',None)

        if payment_method_id is not None and amount is not None and screenshot is not None and sender_number is not None:

            payment_method_obj = PaymentMethod.objects.filter(id=payment_method_id).first()
            if payment_method_obj:
                deposit_request_obj = DepositRequest()
                deposit_request_obj.user = user
                deposit_request_obj.payment_method = payment_method_obj
                deposit_request_obj.amount = amount
                deposit_request_obj.sender_number = sender_number
                deposit_request_obj.transaction_id = transaction_id

                compressed_image = compress(screenshot)
                # Choosing smaller image size
                if compressed_image.size > screenshot.size:
                    compressed_image = screenshot
                deposit_request_obj.screenshot = compressed_image

                deposit_request_obj.save()
                # serializer_deposit_request = DepositRequestSerializer(instance=deposit_request_obj,context={'request': request})
                return Response(status=HTTP_201_CREATED)

        return Response(status=HTTP_204_NO_CONTENT)

class WithdrawRequestListApiView(ListAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        user = request.user
        withdraw_request_objs = WithdrawRequest.objects.filter(user=user)
        serializer_withdraw_request_list = WithdrawRequestSerializer(instance=withdraw_request_objs,many=True,context={'request': request})

        return Response({'withdraw_request_list':serializer_withdraw_request_list.data,},status=HTTP_200_OK)

class WithdrawRequestCreateApiView(CreateAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        data_obj = request.data
        user = request.user

        payment_method_id = data_obj.get('payment_method',None)
        amount = data_obj.get('amount',None)
        received_amount = data_obj.get('received_amount',None)
        receiver_number = data_obj.get('receiver_number',None)

        if payment_method_id is not None and amount is not None and received_amount is not None and receiver_number is not None:
            balance_obj = Balance.objects.filter(user=user).first()
            # No sufficient amount to withdraw
            if balance_obj is None or balance_obj.earn_amount < amount:
                return Response(status=HTTP_203_NON_AUTHORITATIVE_INFORMATION)

            payment_method_obj = PaymentMethod.objects.filter(id=payment_method_id).first()
            if payment_method_obj:
                withdraw_request_obj = WithdrawRequest()
                withdraw_request_obj.user = user
                withdraw_request_obj.payment_method = payment_method_obj
                withdraw_request_obj.amount = amount
                withdraw_request_obj.received_amount = received_amount
                withdraw_request_obj.receiver_number = receiver_number
                withdraw_request_obj.save()
                # serializer_withdraw_request = WithdrawRequestSerializer(instance=withdraw_request_obj,context={'request': request})
                return Response(status=HTTP_201_CREATED)

        return Response(status=HTTP_204_NO_CONTENT)
