
from django.conf.urls import url
from django.conf.urls import include
from rest_framework.routers import DefaultRouter
from .views import MemberViewSet

router = DefaultRouter()
router.register(r'info', MemberViewSet, base_name='member')

urlpatterns = [
    url(r'', include(router.urls)),
]