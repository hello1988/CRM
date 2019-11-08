from django.utils import timezone
from .models import Member, Operator, Product, Order, Cart, Coupon, CouponTable
from django.dispatch import receiver
from django.db.models.signals import post_save
from social_django.models import UserSocialAuth
from django.db.models import Q

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

    def update_info(self, user, first_name, last_name, phone, email, birth):
        member = self.get_by_user(user)
        member.first_name = first_name
        member.last_name = last_name
        member.phone = phone
        member.email = email

        birth = birth
        if birth.count('/') == 2:
            year, month, day = birth.split('/')
            member.birth_year = year
            member.birth_month = month
            member.birth_day = day

        member.registered = True
        member.save()
        return member

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

    def get_product_map(self):
        result = {}
        for product in self.get_all():
            result[product.id] = product

        return result

class OrderRepo(object):
    def create_order(self, member, operator, form_data):
        carts = []
        product_map = product_repo.get_product_map()
        idx = 0
        total = 0
        while(True):
            product_id = form_data.get('product%s'%(idx,), None )
            quantity = form_data.get('quantity%s'%(idx,), None )
            idx += 1
            if product_id is None:
                break

            if not product_id.isdigit() or not quantity.isdigit():
                continue

            product = product_map.get(int(product_id), None)
            if not product:
                continue

            carts.append( Cart(member=member, operator=operator, product=product, quantity=quantity) )
            total += product.price*int(quantity)

        if len(carts) <= 0:
            return

        order = Order.objects.create(member=member)
        coupon_id = form_data.get('coupon')
        coupon = coupon_repo.use_coupon(member, coupon_id)
        if coupon:
            if coupon.coupon.discount_percentage > 0:
                total *= coupon.coupon.discount_percentage

            elif coupon.coupon.discount_value > 0:
                total -= coupon.coupon.discount_value

        discount = int( form_data.get('discount', 0) )
        order.total_price = total - discount
        order.discount = discount
        order.save()

        for cart in carts:
            cart.order = order

        Cart.objects.bulk_create(carts)

class CouponRepo(object):
    # Coupon, CouponTable
    def get_coupon_by_member(self, member, available=None):
        coupons = CouponTable.objects.filter(member=member)
        if available:
            coupons = coupons.filter(available=available)
            coupons = coupons.filter( Q(expired_at__isnull=True) | Q(expired_at__gt=timezone.now())  )
        return coupons

    def use_coupon(self, member, coupon_id):
        coupons = CouponTable.objects.filter(member=member, id=coupon_id)
        coupon = CouponTable.objects.filter(member=member, id=coupon_id).first()
        if not coupon:
            return

        if not coupon.is_available():
            return

        coupon.available = False
        coupon.used_at = timezone.now()
        coupon.save()
        return coupon


member_repo = MemberRepo()
operator_repo = OperatorRepo()
product_repo = ProductRepo()
order_repo = OrderRepo()
coupon_repo = CouponRepo()

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

@receiver(post_save, sender=CouponTable)
def on_member_gain_coupon(sender, instance, created, **kwargs):
    ct = instance
    if created:
        ct.expired_at = ct.coupon.expired_at
        ct.save()