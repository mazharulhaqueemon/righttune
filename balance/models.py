import uuid
import os 
from django.utils import timezone
from django.db import models
from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver 
from accounts.models import User
from balance.utils import (
    custom_unique_slug_generator_for_title,
) 

def payment_method_logo_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f'{uuid.uuid4()}.{ext}'

    return os.path.join('balance/payment_method_logos/',filename) 

def deposit_screenshot_image_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f'{uuid.uuid4()}.{ext}'

    return os.path.join('balance/deposit_screenshot_images/',filename) 

class Balance(models.Model): 
    user = models.OneToOneField(User,on_delete=models.CASCADE) 
    amount = models.DecimalField(max_digits=20,decimal_places=2,default=0.0)
    earn_amount = models.DecimalField(max_digits=6,decimal_places=2,default=0.0)    
    updated_datetime = models.DateTimeField(auto_now_add=False,auto_now=False,blank=True,null=True)

    class Meta:
        verbose_name_plural = 'User Balance'
        ordering = ['-id']

    def __str__(self):
        return f"{self.user.profile.full_name} > Balance: {self.amount} > Updated: {str(self.updated_datetime).split('.')[0]}"


class EarnCoinExchanger(models.Model):
    per_coin_rate = models.DecimalField(max_digits=8,decimal_places=2,default=0.20)

    def __str__(self):
        return f"1 coins = {self.per_coin_rate} BDT"

class PaymentMethod(models.Model): 
    title = models.CharField(max_length=50)
    # Custom Slug
    slug = models.CharField(max_length=80,unique=True,blank=True,null=True)
    logo   = models.ImageField(upload_to=payment_method_logo_path)

    account_number = models.CharField(max_length=50)
    percent_charge = models.DecimalField(max_digits=6,decimal_places=2,default=0.0)    
    is_receive_transaction_id = models.BooleanField(default=True)

    created_datetime = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Payment Methods'
        ordering = ['id']

    def __str__(self):
        return f"{self.title} > {self.account_number} > Charge: {self.percent_charge}%" 

class DepositRequest(models.Model): 
    user = models.ForeignKey(User,on_delete=models.CASCADE) 
    payment_method = models.ForeignKey(PaymentMethod,on_delete=models.SET_NULL,blank=True,null=True)

    screenshot   = models.ImageField(upload_to=deposit_screenshot_image_path)
    amount = models.DecimalField(max_digits=6,decimal_places=2)    
    sender_number = models.CharField(max_length=50)
    transaction_id = models.CharField(max_length=50,null=True,blank=True)
    feedback = models.CharField(max_length=350,null=True,blank=True)

    is_pending = models.BooleanField(default=True)
    is_accepted = models.BooleanField(default=False)
    is_declined = models.BooleanField(default=False)

    requested_datetime = models.DateTimeField(auto_now_add=True)
    updated_datetime = models.DateTimeField(auto_now_add=False,auto_now=False,null=True,blank=True)

    def save(self, *args, **kwargs):
        # Restrict user not to update again
        if self.updated_datetime is not None:
            return
        if self.is_accepted:
            balance_obj = Balance.objects.filter(user=self.user).first()
            if balance_obj is None:
                balance_obj = Balance() 
                balance_obj.user = self.user
                balance_obj.amount = self.amount
            else:
                balance_obj.amount += self.amount
            balance_obj.updated_datetime = timezone.now()
            balance_obj.save()
            self.updated_datetime = timezone.now()
        elif self.is_declined:
            self.updated_datetime = timezone.now()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name_plural = 'Deposit Requests'
        ordering = ['-id']

    def __str__(self):
        status = ''        
        if self.is_accepted == True:
            status = 'Accepted'
        elif self.is_declined == True:
            status = 'Declined'
        elif self.is_pending == True:
            status = 'Pending'
        return f"{self.user.profile.full_name} > {str(self.requested_datetime).split('.')[0]} > {status}"

class WithdrawRequest(models.Model): 
    user = models.ForeignKey(User,on_delete=models.CASCADE) 
    payment_method = models.ForeignKey(PaymentMethod,on_delete=models.SET_NULL,blank=True,null=True)

    amount = models.DecimalField(max_digits=6,decimal_places=2)    
    received_amount = models.DecimalField(max_digits=6,decimal_places=2)    
    receiver_number = models.CharField(max_length=50)
    feedback = models.CharField(max_length=350,null=True,blank=True)
    
    is_pending = models.BooleanField(default=True)
    is_accepted = models.BooleanField(default=False)
    is_declined = models.BooleanField(default=False)

    requested_datetime = models.DateTimeField(auto_now_add=True)
    updated_datetime = models.DateTimeField(auto_now_add=False,auto_now=False,null=True,blank=True)

    def save(self, *args, **kwargs):
        # Restrict user not to update again
        if self.updated_datetime is not None:
            return
        if self.is_accepted:
            balance_obj = Balance.objects.filter(user=self.user).first()
            if balance_obj:
                balance_obj.amount -= self.amount
                balance_obj.updated_datetime = timezone.now()
                balance_obj.save()
                self.updated_datetime = timezone.now()
            else:
                return
        elif self.is_declined:
            self.updated_datetime = timezone.now()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name_plural = 'Withdraw Requests'
        ordering = ['-id']

    def __str__(self):
        status = ''
        if self.is_accepted == True:
            status = 'Accepted'
        elif self.is_declined == True:
            status = 'Declined'
        elif self.is_pending == True:
            status = 'Pending'
        return f"{self.user.profile.full_name} > {str(self.requested_datetime).split('.')[0]} > {status}"

class Plan(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=6,decimal_places=2)    
    minutes = models.IntegerField(default=0)
    days = models.IntegerField(verbose_name='Validity Days',default=0)

    class Meta:
        ordering = ['price']

    def __str__(self):
        return f"{self.name} > Minutes: {self.minutes} > Price: {self.price} > Validity: {self.days} days"

class PlanPurchased(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    plan = models.ForeignKey(Plan,on_delete=models.CASCADE)
    minutes = models.DecimalField(max_digits=10,decimal_places=2)    
    expired_datetime = models.DateTimeField(auto_now_add=False,auto_now=False,null=True,blank=True)

    class Meta:
        verbose_name_plural = 'Plan Purchased'
        ordering = ['expired_datetime']

    def __str__(self):
        return f"{self.user.profile.full_name} > Plan: {self.plan.name} > Validity: {str(self.expired_datetime).split('.')[0]}"

class EarnMinuteExchanger(models.Model): 
    per_minute_rate = models.DecimalField(max_digits=8,decimal_places=2,default=0.20)    

    def save(self, *args, **kwargs):
        if EarnMinuteExchanger.objects.last() is not None:
            return
        super().save(*args, **kwargs)

    class Meta:
        verbose_name_plural = "Earn Minute Exchanger Rule (in BDT) on InCome call (Don't add multiple rule)"

    def __str__(self):
        return f"1 minute = {self.per_minute_rate} BDT"

class EarningHistory(models.Model): 
    user = models.ForeignKey(User,on_delete=models.CASCADE) 
    earn_amount = models.DecimalField(max_digits=6,decimal_places=2,default=0.0)    
    date = models.DateField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Earning Histories'
        ordering = ['-date']

    def __str__(self):
        return f"{self.user.profile.full_name} > Earn: {self.earn_amount} > Date: {str(self.date).split('.')[0]}"

pre_save.connect(custom_unique_slug_generator_for_title, sender=PaymentMethod)

@receiver(post_delete,sender=PaymentMethod)
def payment_method_submission_delete(sender,instance,**kwargs):
    instance.logo.delete(False)

@receiver(post_delete,sender=DepositRequest)
def deposit_request_submission_delete(sender,instance,**kwargs):
    instance.screenshot.delete(False)
