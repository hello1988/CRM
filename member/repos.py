from .models import Member, Operator, Product
from django.dispatch import receiver
from django.db.models.signals import post_save
from social_django.models import UserSocialAuth

class MemberRepo(object):
    def get_by_social(self, social_user):

        member, created = Member.objects.get_or_create(social_user=social_user)
        return member

    def get_by_user(self, user):
        try:
            member = Member.objects.get(user=user)
            return member
        except:
            return None

    def get_by_phone(self, phone):
        try:
            member = Member.objects.get(phone=phone)
            return member
        except:
            return None

class OperatorRepo(object):
    def get_by_user(self, user):
        try:
            operator = Operator.objects.get(user=user)
            return operator
        except:
            return None

class ProductRepo(object):
    def get_all(self):
        return Product.objects.all()

member_repo = MemberRepo()
operator_repo = OperatorRepo()
product_repo = ProductRepo()

@receiver(post_save, sender=UserSocialAuth)
def on_user_create(sender, instance, created, **kwargs):
    social_user = instance
    member = member_repo.get_by_social(social_user)
    if created:
        member.user = social_user.user

    if 'id' in social_user.extra_data:
        extra_data = social_user.extra_data
        member.line_id = extra_data['id']
        member.picture_url = extra_data.get('picture_url', '')
        member.status_message = extra_data.get('status_message', '')

    member.save()