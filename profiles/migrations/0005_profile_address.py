# Generated by Django 3.2.4 on 2022-10-05 09:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0004_profile_about'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='address',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
    ]