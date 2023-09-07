from django.contrib import admin
from django.contrib.auth.models import User, Group
from rest_framework.authtoken.models import Token
from .models import (
    PaymentMethod,DepositRequest,WithdrawRequest,Balance,Plan,EarnMinuteExchanger,
    PlanPurchased,EarningHistory, EarnCoinExchanger
    )

admin.site.site_header = "Metazo Admin"
admin.site.site_title = "Metazo Admin"
admin.site.index_title = "Welcome to Metazo"
# admin.site.unregister(User)
# admin.site.unregister(Group)
# admin.site.unregister(Token)
admin.site.register(EarnCoinExchanger)
admin.site.register(PaymentMethod)
admin.site.register(DepositRequest)
admin.site.register(WithdrawRequest)
admin.site.register(Balance)
admin.site.register(Plan)
admin.site.register(EarnMinuteExchanger)
admin.site.register(PlanPurchased)
admin.site.register(EarningHistory)