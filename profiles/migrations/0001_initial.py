# Generated by Django 3.2.4 on 2023-11-19 11:27

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import profiles.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Assets',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=200)),
                ('level', models.CharField(blank=True, max_length=200)),
                ('price', models.CharField(max_length=200)),
                ('animation_image', models.ImageField(blank=True, null=True, upload_to=profiles.models.profile_asset_path)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='FrameStore',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='frames/')),
                ('title', models.CharField(max_length=100)),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
            ],
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('full_name', models.CharField(max_length=200)),
                ('slug', models.CharField(blank=True, max_length=250, null=True, unique=True)),
                ('email', models.EmailField(blank=True, max_length=250, null=True)),
                ('profile_image', models.ImageField(blank=True, null=True, upload_to=profiles.models.profile_image_path)),
                ('cover_image', models.ImageField(blank=True, null=True, upload_to=profiles.models.cover_image_path)),
                ('birthday', models.DateField(blank=True, null=True)),
                ('gender', models.CharField(blank=True, max_length=20, null=True)),
                ('iso_code', models.CharField(blank=True, max_length=250, null=True)),
                ('iso3_code', models.CharField(blank=True, max_length=250, null=True)),
                ('phone_code', models.CharField(blank=True, max_length=250, null=True)),
                ('country_name', models.CharField(blank=True, max_length=250, null=True)),
                ('mobile_number', models.CharField(blank=True, max_length=250, null=True)),
                ('streaming_title', models.CharField(blank=True, max_length=250, null=True)),
                ('earn_coins', models.IntegerField(default=0)),
                ('earn_loves', models.IntegerField(default=0)),
                ('registered_date', models.DateField(auto_now_add=True)),
                ('updated_date', models.DateField(blank=True, null=True)),
                ('blocked_users', models.ManyToManyField(blank=True, db_constraint=False, related_name='blocked_by', to=settings.AUTH_USER_MODEL)),
                ('followers', models.ManyToManyField(blank=True, db_constraint=False, related_name='following_profile', to=settings.AUTH_USER_MODEL)),
                ('friends', models.ManyToManyField(blank=True, db_constraint=False, related_name='friends_profile', to=settings.AUTH_USER_MODEL)),
                ('user', models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Stories',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('caption', models.CharField(blank=True, max_length=250, null=True)),
                ('user_profile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_profile', to='profiles.profile')),
            ],
        ),
        migrations.CreateModel(
            name='UserAssets',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=200)),
                ('level', models.CharField(max_length=200)),
                ('animation_image', models.CharField(blank=True, max_length=300, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('frame_store', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='profiles.framestore')),
                ('user', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='StoryImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(blank=True, null=True, upload_to=profiles.models.story_image)),
                ('stories', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='post_stories', to='profiles.stories')),
            ],
        ),
        migrations.CreateModel(
            name='Follow',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_followed', models.DateTimeField(auto_now_add=True)),
                ('follower', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='following_userfollower', to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='followers', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
