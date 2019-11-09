from django.shortcuts import render
from django.http import JsonResponse
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth.mixins import LoginRequiredMixin
from rest_framework.authentication import BasicAuthentication, TokenAuthentication
from .repos import member_repo, operator_repo, product_repo, order_repo, coupon_repo
from dateutil.parser import parse as dt_parse
from pytz import timezone
from django.conf import settings
# Create your views here.
class MemberViewSet(LoginRequiredMixin, viewsets.ViewSet):
    # authentication_classes = ()
    permission_classes = (permissions.IsAuthenticated,)
    # renderer_classes = (TemplateHTMLRenderer,)
    login_url = '/oauth/login/line'

    @action(methods=['get', 'post'], detail=False, url_path='home')
    def home(self, request):
        if request.method == 'GET':
            member = member_repo.get_by_user(request.user)
            if not member.registered:
                return render(request, 'registered.html', {})

            else:
                host = request.META['HTTP_HOST']
                uri = 'http://' if host.startswith('localhost') else 'https://'
                uri += host
                return render(request, 'home.html', {'member':member, 'uri':uri})

        elif request.method == 'POST':
            data = request.POST.dict()
            if not all(key in data for key in ['first_name', 'last_name', 'phone', 'birth']):
                return render(request, 'registered.html', {})

            member = member_repo.update_info(request.user, data['first_name'], data['last_name'], data['phone'],
                                             data.get('email', ''), data['birth'])

            host = request.META['HTTP_HOST']
            uri = 'http://' if host.startswith('localhost') else 'https://'
            uri += host
            return render(request, 'home.html', {'member': member, 'uri': uri})

        return Response(status.HTTP_200_OK)


    @action(methods=['get', 'post'], detail=False, url_path='edit')
    def edit(self, request):
        if request.method == 'GET':
            member = member_repo.get_by_user(request.user)
            if not member.registered:
                return render(request, 'registered.html', {})

            else:
                return render(request, 'member_edit.html', {'member':member})

        elif request.method == 'POST':
            data = request.POST.dict()
            if not all(key in data for key in ['first_name', 'last_name', 'phone', 'birth']):
                return Response(status.HTTP_200_OK)

            member = member_repo.update_info(request.user, data['first_name'], data['last_name'], data['phone'],
                                             data.get('email', ''), data['birth'])
            return render(request, 'home.html', {'member': member})

        return Response(status.HTTP_200_OK)

    @action(methods=['get'], detail=False, url_path='coupon')
    def coupon(self, request):
        member = member_repo.get_by_user(request.user)
        coupons = coupon_repo.get_coupon_by_member(member, available=True)
        result = self.__coupon_serialize(coupons)
        return JsonResponse(result, safe=False)

    def __coupon_serialize(self, coupons):
        result = []
        for coupon in coupons:
            info = {}
            info['id'] = coupon.id
            info['name'] = coupon.coupon.name
            info['desc'] = coupon.coupon.desc
            info['expired_at'] = coupon.expired_at.strftime('%Y/%m/%d') if coupon.expired_at else ''

            result.append(info)

        return result

    @action(methods=['get'], detail=False, url_path='record')
    def record(self, request):
        start_dt = request.GET.get('start_dt', None)
        end_dt = request.GET.get('end_dt', None)

        tz_info = timezone(settings.TIME_ZONE)
        if start_dt:
            start_dt  = dt_parse(start_dt).replace(tzinfo=tz_info)

        if end_dt:
            end_dt = dt_parse(end_dt).replace(tzinfo=tz_info)

        orders = order_repo.get_by_user(request.user, start_dt=start_dt, end_dt=end_dt)
        result = order_repo.get_orders_detail(orders)
        return JsonResponse(result, safe=False)

class TransactionViewSet(viewsets.ViewSet):
    authentication_classes = (BasicAuthentication, TokenAuthentication,)
    permission_classes = (permissions.IsAdminUser,)

    @action(methods=['post'], detail=False, url_path='query_member')
    def query_member(self, request):
        data = request.POST.dict()
        phone = data.get('phone','')
        member = member_repo.get_by_phone(phone)
        result = {}
        if member:
            result['name'] = '{} {}'.format(member.first_name, member.last_name,)
            result['points'] = member.remain_points
            result['birth'] = '{}/{}/{}'.format(member.birth_year, member.birth_month, member.birth_day)

        coupon_info = {}
        coupon_list = []
        coupons = coupon_repo.get_coupon_by_member(member, available=True)
        for coupon in coupons:
            coupon_info[coupon.id] = {'id':coupon.id, 'percentage':coupon.coupon.discount_percentage, 'value':coupon.coupon.discount_value}

            expired_at = coupon.expired_at.strftime('%Y/%m/%d') if coupon.expired_at else ''
            coupon_list.append( {'id':coupon.id, 'name':coupon.coupon.name, 'expired_at':expired_at} )

        result['coupon_info'] = coupon_info
        result['coupons'] = coupon_list
        return JsonResponse(result)


    @action(methods=['get'], detail=False, url_path='record')
    def record(self, request):
        phone = request.GET.get('phone', '')
        member = member_repo.get_by_phone(phone)
        orders = order_repo.get_by_member(member)
        result = order_repo.get_orders_detail(orders)
        return JsonResponse(result, safe=False)

    @action(methods=['get', 'post'], detail=False, url_path='checkout')
    def checkout(self, request):
        if request.method == 'GET':
            phone = request.GET.get('phone', '')
            member = member_repo.get_by_phone(phone)
            products = product_repo.get_all()
            coupons = coupon_repo.get_coupon_by_member(member, available=True)
            return render(request, 'checkout.html', {'member':member, 'products':products, 'coupons':coupons})

        elif request.method == 'POST':
            data = request.POST.dict()
            phone = data.get('phone','')
            member = member_repo.get_by_phone(phone)
            operator = operator_repo.get_by_user(request.user)
            if not member or not operator:
                return Response(status.HTTP_400_BAD_REQUEST)

            order_repo.create_order(member, operator, data)

            result = {'success':1}
            return JsonResponse(result)

        return Response(status.HTTP_200_OK)


class CouponViewSet(viewsets.ViewSet):
    authentication_classes = (BasicAuthentication, TokenAuthentication,)
    permission_classes = (permissions.IsAdminUser,)

    @action(methods=['get'], detail=False, url_path='list')
    def get_all(self, request):
        result = []
        return JsonResponse(result, safe=False)

    @action(methods=['post'], detail=False, url_path='create')
    def create_coupon(self, request):
        return Response(status.HTTP_200_OK)

    @action(methods=['post'], detail=False, url_path='modify')
    def modify_coupon(self, request):
        return Response(status.HTTP_200_OK)

    @action(methods=['post'], detail=False, url_path='member_gain')
    def member_gain(self, request):
        result = {}
        return JsonResponse(result)

    @action(methods=['post'], detail=False, url_path='member_update')
    def member_update(self, request):
        result = {}
        return JsonResponse(result)