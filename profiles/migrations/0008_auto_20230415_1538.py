# Generated by Django 3.2.4 on 2023-04-15 09:38

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('profiles', '0007_stories_storyimage'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='blocked_users',
            field=models.ManyToManyField(related_name='blocked_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='profile',
            name='friends',
            field=models.ManyToManyField(related_name='friends_profile', to=settings.AUTH_USER_MODEL),
        ),
    ]
