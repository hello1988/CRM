from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Basis(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Member(Basis):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=32, null=True, default=None, blank=True)
    email = models.CharField(max_length=128, null=True, default=None, blank=True)

    # user = models.ForeignKey(User, on_delete=models.CASCADE)
    # line_id = models.CharField(max_length=128, default='')
    #
    # birth_year = models.PositiveIntegerField(default=0)
    # birth_month = models.PositiveIntegerField(default=0)
    # birth_day = models.PositiveIntegerField(default=0)
    #
    # remain_points = models.PositiveIntegerField(default=0)