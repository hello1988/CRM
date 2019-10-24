from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User
from social_django.models import UserSocialAuth


# Create your models here.
class Basis(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

# 會員
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

    birth_year = models.PositiveIntegerField(default=0, blank=True)
    birth_month = models.PositiveIntegerField(default=0, blank=True)
    birth_day = models.PositiveIntegerField(default=0, blank=True)

    remain_points = models.PositiveIntegerField(default=0, blank=True)

    def __unicode__(self):
        return '{} {}'.format(self.first_name, self.last_name)

    def __str__(self):
        return '{} {}'.format(self.first_name, self.last_name)

# 施術者
class Operator(Basis):
    first_name = models.CharField(max_length=255, default='', blank=True)
    last_name = models.CharField(max_length=255, default='', blank=True)
    phone = models.CharField(max_length=32, null=True, default=None, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __unicode__(self):
        return '{} {}'.format(self.first_name, self.last_name)


    def __str__(self):
        return '{} {}'.format(self.first_name, self.last_name)

# 診斷紀錄
class MedicalRecord(Basis):
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    operator = models.ForeignKey(Operator, on_delete=models.CASCADE)
    title = models.CharField(max_length=32, default='', blank=True)
    text = models.TextField(default='', blank=True)

    def __unicode__(self):
        return self.title


    def __str__(self):
        return self.title

# 產品、課程
class Product(models.Model):
    name = models.CharField(max_length=32)
    desc = models.CharField(max_length=256)
    price = models.PositiveIntegerField(default=0)

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name

class Coupon(models.Model):
    name = models.CharField(max_length=32)
    desc = models.CharField(max_length=256)
    discount_percentage = models.FloatField(default=0.0, null=True, blank=True)
    discount_value = models.PositiveIntegerField(default=0, null=True, blank=True)
    expired_at = models.DateTimeField(null=True, blank=True)

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name

class CouponTable(Basis):
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE)
    expired_at = models.DateTimeField(null=True, blank=True)
    used_at = models.DateTimeField(null=True, blank=True)
    available = models.BooleanField(default=True)

    def is_available(self):
        if self.available == False:
            return False

        if self.expired_at is not None and self.expired_at < timezone.now():
            return False

        return True

class Order(Basis):
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    discount = models.PositiveIntegerField(default=0)
    total_price = models.PositiveIntegerField(default=0)
    coupon = models.ForeignKey(CouponTable, on_delete=models.CASCADE, null=True, default=None, blank=True)

class Cart(Basis):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    operator = models.ForeignKey(Operator, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0)