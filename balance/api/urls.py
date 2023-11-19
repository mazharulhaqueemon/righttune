from django.urls import path
from .views import (
    PaymentMethodListApiView,BalanceRetrieveApiView,
    DepositRequestCreateApiView,WithdrawRequestCreateApiView,
    DepositRequestListApiView, WithdrawRequestListApiView,
    PlanListApiView,PlanPurchasedListApiView,PlanPurchasedCreateApiView,
    PlanPurchasedRemaingMinutesRetrieveApiView,PaidForCallCreateApiView,
    DashboardRetrieveApiView,WalletRetrieveApiView,
)

urlpatterns = [
    path('payment-method-list/',PaymentMethodListApiView.as_view()),
    path('balance-retrieve/',BalanceRetrieveApiView.as_view()),
    path('deposit-request-list/',DepositRequestListApiView.as_view()),
    path('deposit-request-create/',DepositRequestCreateApiView.as_view()),
    path('withdraw-request-list/',WithdrawRequestListApiView.as_view()),
    path('withdraw-request-create/',WithdrawRequestCreateApiView.as_view()),
    # Plan
    path('plan-list/',PlanListApiView.as_view()),
    path('purchased-plan-list/',PlanPurchasedListApiView.as_view()),
    path('plan-purchased-create/',PlanPurchasedCreateApiView.as_view()),
    path('check-for-call-allowed/',PlanPurchasedRemaingMinutesRetrieveApiView.as_view()),
    path('paid-for-call-create/',PaidForCallCreateApiView.as_view()),
    # Account
    path('my-dashboard/',DashboardRetrieveApiView.as_view()),
    path('my-wallet/',WalletRetrieveApiView.as_view()),
]