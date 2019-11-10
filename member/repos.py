from django.utils import timezone
from .models import Member, Operator, Product, Order, Cart, Coupon, CouponTable, MedicalRecord
from django.dispatch import receiver
from django.db.models.signals import post_save
from social_django.models import UserSocialAuth
from django.db.models import Q
from dateutil.relativedelta import relativedelta

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
        medical_record_repo.create(member, operator, order)

    def get_by_user(self, user, start_dt=None, end_dt=None):
        member = member_repo.get_by_user(user)

        if end_dt is None:
            end_dt = timezone.now()

        if start_dt is None:
            start_dt = end_dt + relativedelta(months=-3)

        orders = Order.objects.filter(member=member, created_at__range=(start_dt, end_dt)).order_by('-created_at')
        return orders

    def get_by_member(self, member):
        orders = Order.objects.filter(member=member).order_by('-created_at')
        return orders

    def get_orders_detail(self, orders):
        order_ids = orders.values_list('id', flat=True)
        carts = Cart.objects.filter(order__in=order_ids)

        cart_info = {}
        for cart in carts:
            order_id = cart.order.id
            if order_id not in cart_info:
                cart_info[order_id] = []

            data = {'product':cart.product.name, 'quantity':cart.quantity}
            cart_info[order_id].append(data)

        records = medical_record_repo.get_by_order_ids(order_ids)
        record_info = { record['order_id']:record['id'] for record in records.values('order_id', 'id') }

        result = []
        for order in orders:
            info = {}
            info['order_id'] = order.id
            info['discount'] = order.discount
            info['total_price'] = order.total_price
            info['coupon'] = order.coupon.coupon.name if order.coupon else ''
            info['created_at'] = order.created_at.strftime('%Y/%m/%d %H:%M')
            info['products'] = cart_info.get(order.id, [])
            info['record_id'] = record_info.get(order.id, '')

            result.append(info)

        return result

class CouponRepo(object):
    # Coupon, CouponTable
    def modify_coupon(self, name, desc, percentage, value, expired_dt=None, coupon_id=None):
        coupon = Coupon()
        if coupon_id:
            coupon = Coupon.objects.filter(id=coupon_id).first()
            if coupon is None:
                return

        coupon.name = name
        coupon.desc = desc
        coupon.discount_percentage = percentage
        coupon.discount_value = value
        if expired_dt:
            coupon.expired_dt = expired_dt
        coupon.save()
        return coupon

    def get_all(self):
        coupons = Coupon.objects.all()
        return coupons

    def modify_member_coupon(self, member, coupon_id=None, available=None, expired_at=None, ct_id=None):
        coupon_t = CouponTable()
        if ct_id:
            coupon_t = CouponTable.objects.filter(id=ct_id).first()
            if coupon_t is None:
                return

        coupon_t.member = member
        if coupon_id:
            coupon_t.coupon_id = coupon_id

        if expired_at:
            coupon_t.expired_at = expired_at

        if available is not None:
            coupon_t.available = available

        coupon_t.save()
        return coupon_t

    def get_coupon_by_member(self, member, available=None):
        coupons = CouponTable.objects.filter(member=member)
        if available:
            coupons = coupons.filter(available=available)
            coupons = coupons.filter( Q(expired_at__isnull=True) | Q(expired_at__gt=timezone.now())  )
        return coupons.order_by('expired_at')

    def use_coupon(self, member, coupon_id):
        coupon = CouponTable.objects.filter(member=member, id=coupon_id).first()
        if not coupon:
            return

        if not coupon.is_available():
            return

        coupon.available = False
        coupon.used_at = timezone.now()
        coupon.save()
        return coupon

class MedicalRecordRepo(object):
    def create(self, member, operator, order):
        record = MedicalRecord.objects.create(member=member, operator=operator, order=order, title='尚未輸入')
        return record

    def get_by_id(self, record_id):
        record = MedicalRecord.objects.filter(id=record_id).first()
        return record

    def get_by_order_ids(self, order_ids):
        records = MedicalRecord.objects.filter(order_id__in=order_ids)
        return records

    def modify(self, record_id, **kwargs):
        record = self.get_by_id(record_id)
        if not record:
            return

        fields = MedicalRecord._meta.get_fields()
        editable_fields = { field.name for field in fields if field.get_internal_type() in {'CharField', 'TextField', 'BooleanField',} }
        bool_fields = { field.name for field in fields if field.get_internal_type() in {'BooleanField',} }
        for attr, value in kwargs.items():
            if attr not in editable_fields:
                continue

            if attr in bool_fields:
                value = True if value == 'true' else False

            setattr( record, attr, value )

        record.save()
        return record

member_repo = MemberRepo()
operator_repo = OperatorRepo()
product_repo = ProductRepo()
order_repo = OrderRepo()
coupon_repo = CouponRepo()
medical_record_repo = MedicalRecordRepo()

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