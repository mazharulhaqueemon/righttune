# Generated by Django 3.2.4 on 2023-11-19 11:27

import balance.models
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='EarnCoinExchanger',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('per_coin_rate', models.DecimalField(decimal_places=2, default=0.2, max_digits=8)),
            ],
        ),
        migrations.CreateModel(
            name='EarnMinuteExchanger',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('per_minute_rate', models.DecimalField(decimal_places=2, default=0.2, max_digits=8)),
            ],
            options={
                'verbose_name_plural': "Earn Minute Exchanger Rule (in BDT) on InCome call (Don't add multiple rule)",
            },
        ),
        migrations.CreateModel(
            name='PaymentMethod',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=50)),
                ('slug', models.CharField(blank=True, max_length=80, null=True, unique=True)),
                ('logo', models.ImageField(upload_to=balance.models.payment_method_logo_path)),
                ('account_number', models.CharField(max_length=50)),
                ('percent_charge', models.DecimalField(decimal_places=2, default=0.0, max_digits=6)),
                ('is_receive_transaction_id', models.BooleanField(default=True)),
                ('created_datetime', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name_plural': 'Payment Methods',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='Plan',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('price', models.DecimalField(decimal_places=2, max_digits=6)),
                ('minutes', models.IntegerField(default=0)),
                ('days', models.IntegerField(default=0, verbose_name='Validity Days')),
            ],
            options={
                'ordering': ['price'],
            },
        ),
        migrations.CreateModel(
            name='WithdrawRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=6)),
                ('received_amount', models.DecimalField(decimal_places=2, max_digits=6)),
                ('receiver_number', models.CharField(max_length=50)),
                ('feedback', models.CharField(blank=True, max_length=350, null=True)),
                ('is_pending', models.BooleanField(default=True)),
                ('is_accepted', models.BooleanField(default=False)),
                ('is_declined', models.BooleanField(default=False)),
                ('requested_datetime', models.DateTimeField(auto_now_add=True)),
                ('updated_datetime', models.DateTimeField(blank=True, null=True)),
                ('payment_method', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='balance.paymentmethod')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'Withdraw Requests',
                'ordering': ['-id'],
            },
        ),
        migrations.CreateModel(
            name='PlanPurchased',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('minutes', models.DecimalField(decimal_places=2, max_digits=10)),
                ('expired_datetime', models.DateTimeField(blank=True, null=True)),
                ('plan', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='balance.plan')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'Plan Purchased',
                'ordering': ['expired_datetime'],
            },
        ),
        migrations.CreateModel(
            name='EarningHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('earn_amount', models.DecimalField(decimal_places=2, default=0.0, max_digits=6)),
                ('date', models.DateField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'Earning Histories',
                'ordering': ['-date'],
            },
        ),
        migrations.CreateModel(
            name='DepositRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('screenshot', models.ImageField(upload_to=balance.models.deposit_screenshot_image_path)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=6)),
                ('sender_number', models.CharField(max_length=50)),
                ('transaction_id', models.CharField(blank=True, max_length=50, null=True)),
                ('feedback', models.CharField(blank=True, max_length=350, null=True)),
                ('is_pending', models.BooleanField(default=True)),
                ('is_accepted', models.BooleanField(default=False)),
                ('is_declined', models.BooleanField(default=False)),
                ('requested_datetime', models.DateTimeField(auto_now_add=True)),
                ('updated_datetime', models.DateTimeField(blank=True, null=True)),
                ('payment_method', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='balance.paymentmethod')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'Deposit Requests',
                'ordering': ['-id'],
            },
        ),
        migrations.CreateModel(
            name='Balance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, default=0.0, max_digits=6)),
                ('earn_amount', models.DecimalField(decimal_places=2, default=0.0, max_digits=6)),
                ('updated_datetime', models.DateTimeField(blank=True, null=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'User Balance',
                'ordering': ['-id'],
            },
        ),
    ]
