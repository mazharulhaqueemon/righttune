import uuid
import os 
from django.db import models
from accounts.models import User
from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver 

def profile_image_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f'{uuid.uuid4()}.{ext}'

    return os.path.join('profiles/profile_images/',filename) 
def profile_image_asset_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f'{uuid.uuid4()}.{ext}'

    return os.path.join('profiles/user_asset/',filename)
def profile_asset_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f'{uuid.uuid4()}.{ext}'

    return os.path.join('profiles/assets/',filename)
def cover_image_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f'{uuid.uuid4()}.{ext}'

    return os.path.join('profiles/cover_images/',filename) 

class Profile(models.Model):
    user = models.OneToOneField(User,null=True, on_delete=models.SET_NULL)
    full_name = models.CharField(max_length=200)
    slug = models.CharField(max_length=250, unique=True, blank=True, null=True)
    email = models.EmailField(max_length=250,blank=True,null=True)
    profile_image = models.ImageField(upload_to=profile_image_path, blank=True, null=True)
    cover_image = models.ImageField(upload_to=cover_image_path, blank=True, null=True)
    birthday = models.DateField(auto_now=False, auto_now_add=False, blank=True, null=True)
    gender = models.CharField(max_length=20, blank=True, null=True)
    iso_code = models.CharField(max_length=250, blank=True, null=True)
    iso3_code = models.CharField(max_length=250, blank=True, null=True)
    phone_code = models.CharField(max_length=250, blank=True, null=True)
    country_name = models.CharField(max_length=250, blank=True, null=True)
    mobile_number = models.CharField(max_length=250, blank=True, null=True)
    streaming_title = models.CharField(max_length=250, blank=True, null=True)
    balance = models.IntegerField(default=0)
    earn_coins = models.IntegerField(default=0)
    earn_loves = models.IntegerField(default=0)
    followers = models.ManyToManyField(User, related_name='following_profile',blank=True,db_constraint=False)
    friends = models.ManyToManyField(User, related_name="friends_profile",blank=True, db_constraint=False)
    blocked_users = models.ManyToManyField(User, related_name='blocked_by',blank=True, db_constraint=False)
    registered_date = models.DateField(auto_now_add=True)
    updated_date = models.DateField(auto_now=False, auto_now_add=False, blank=True, null=True)

    def __str__(self):
        return self.full_name

    def block_user(self, user):
        """
        Adds the specified user to the blocked_users list.
        """
        self.blocked_users.add(user)

    def unblock_user(self, user):
        """
        Removes the specified user from the blocked_users list.
        """
        self.blocked_users.remove(user)

    def is_blocked(self, user):
        """
        Returns True if the specified user is in the blocked_users list.
        """
        return self.blocked_users.filter(id=user.id).exists()

class FrameStore(models.Model):
    image = models.ImageField(upload_to='frames/')  # Assuming images will be uploaded to a 'frames/' directory
    title = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10,decimal_places=2)  # Assuming the price can have up to 10 digits with 2 decimal places

    def __str__(self):
        return self.title

    def delete(self, *args, **kwargs):
        if self.image:
            delete_file(self.image.path)

        super().delete(*args, **kwargs)


class UserAssets(models.Model):
    user = models.OneToOneField(User,null=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=200,blank=True)
    level = models.CharField(max_length=200)
    frame_store = models.ForeignKey(FrameStore, on_delete=models.SET_NULL, null=True, blank=True)
    animation_image = models.CharField(max_length=300,blank=True,null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.profile.full_name



class Assets(models.Model):
    name = models.CharField(max_length=200,blank=True)
    level = models.CharField(max_length=200,blank=True)
    price = models.CharField(max_length=200)
    animation_image = models.ImageField(upload_to=profile_asset_path, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Follow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followers')
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following_userfollower')
    date_followed = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} --> {self.follower}"
def story_image(instance, filename):
    ext = filename.split('.')[-1]
    filename = f'{uuid.uuid4()}.{ext}'

    return os.path.join('profiles/story_image/',filename)
class Stories(models.Model):
    user_profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='user_profile')
    caption = models.CharField(max_length=250, blank=True, null=True)
class StoryImage(models.Model):
    stories = models.ForeignKey(Stories, on_delete=models.CASCADE,related_name='post_stories',null=True)
    image = models.ImageField(upload_to=story_image, blank=True, null=True)


@receiver(post_delete,sender=Profile)
def profile_submission_delete(sender,instance,**kwargs):
    instance.profile_image.delete(False)
    instance.cover_image.delete(False)

def profile_pre_save_receiver(sender,instance, *args, **kwargs):
    if not instance.slug:
        title = instance.full_name.lower()
        words = title.split(' ')
        temp = ''
        for word in words:
            if word.strip() != '':
                word_separation = word.split('-')
                inner_temp = ''
                for x in word_separation:
                    if x.strip() != '':
                        if inner_temp != '':
                            inner_temp += f"-{x.strip()}"
                        else:
                            inner_temp += x.strip()
                if inner_temp != '':
                    if temp != '':
                        temp += f"-{inner_temp}"
                    else:
                        temp += inner_temp
        # Checking for existing slug
        profile_objs = Profile.objects.filter(slug=temp)
        if profile_objs.exists():
            temp += f"-{profile_objs.count()+1}"
        instance.slug = temp

pre_save.connect(profile_pre_save_receiver, sender=Profile)
