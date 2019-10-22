from django.db import models
from django.contrib.auth.models import User
from social_django.models import UserSocialAuth


# Create your models here.
class Basis(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Member(Basis):
    first_name = models.CharField(max_length=255, default='', blank=True)
    last_name = models.CharField(max_length=255, default='', blank=True)
    phone = models.CharField(max_length=32, null=True, default=None, blank=True)
    email = models.CharField(max_length=128, null=True, default=None, blank=True)

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, default=None)
    social_user = models.ForeignKey(UserSocialAuth, on_delete=models.CASCADE, null=True, default=None)
    line_id = models.CharField(max_length=128, default='', blank=True)
    picture_url = models.TextField(default='', blank=True)
    status_message = models.TextField(default='', blank=True)
    registered = models.BooleanField(default=False)

    birth_year = models.PositiveIntegerField(default=0)
    birth_month = models.PositiveIntegerField(default=0)
    birth_day = models.PositiveIntegerField(default=0)

    remain_points = models.PositiveIntegerField(default=0)

    def __unicode__(self):
        return '{} {}'.format(self.first_name, self.last_name)

    def __str__(self):
        return '{} {}'.format(self.first_name, self.last_name)