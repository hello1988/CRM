from .models import Member, Operator, Product, Order, Cart
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
        discount = int( form_data['discount'] )
        order.total_price = total - discount
        order.discount = discount
        order.save()

        for cart in carts:
            cart.order = order

        Cart.objects.bulk_create(carts)


member_repo = MemberRepo()
operator_repo = OperatorRepo()
product_repo = ProductRepo()
order_repo = OrderRepo()

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