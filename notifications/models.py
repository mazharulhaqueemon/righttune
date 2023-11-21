from django.db import models
from accounts.models import User

class Notification(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    from_user = models.ForeignKey(User,on_delete=models.CASCADE,related_name='from_user',blank=True,null=True)
    context = models.CharField(max_length=200)
    datetime = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return f'{self.user.profile.full_name} > {self.datetime}'

class Banner(models.Model):
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to='banners/')