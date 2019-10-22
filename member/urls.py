
from django.conf.urls import url
from django.conf.urls import include
from rest_framework.routers import DefaultRouter
from .views import MemberViewSet, TransactionViewSet

router = DefaultRouter()
router.register(r'info', MemberViewSet, base_name='member')
router.register(r'trans', TransactionViewSet, base_name='transaction')

urlpatterns = [
    url(r'', include(router.urls)),
]