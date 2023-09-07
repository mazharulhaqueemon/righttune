from django.db import models


class last(models.Model):
    text = models.CharField(max_length=200)
    type = models.CharField(max_length=200)

class fast(models.Model):
    text = models.CharField(max_length=200)
    type = models.CharField(max_length=200)

# Create your models here.
