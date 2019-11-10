
from django.conf.urls import url
from django.conf.urls import include
from rest_framework.routers import DefaultRouter
from .views import MemberViewSet, TransactionViewSet, CouponViewSet, RecordViewSet

router = DefaultRouter()
router.register(r'info', MemberViewSet, base_name='member')
router.register(r'trans', TransactionViewSet, base_name='transaction')
router.register(r'coupon', CouponViewSet, base_name='coupon')
router.register(r'record', RecordViewSet, base_name='record')

urlpatterns = [
    url(r'', include(router.urls)),
]