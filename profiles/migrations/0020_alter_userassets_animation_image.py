# Generated by Django 3.2.4 on 2023-05-04 08:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0019_alter_userassets_animation_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userassets',
            name='animation_image',
            field=models.CharField(blank=True, max_length=300, null=True),
        ),
    ]