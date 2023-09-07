from django.db import models
from accounts.models import User

class FavoriteUser(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    favorite_users = models.ManyToManyField(User,related_name='favorite_users')
    datetime = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Favorite Users'
        ordering = ['user__profile__full_name']

    def __str__(self):
        return f'{self.user.phone} > {self.datetime}'