from django.shortcuts import render
from django.http import JsonResponse
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth.mixins import LoginRequiredMixin
from rest_framework.authentication import BasicAuthentication, TokenAuthentication
from .repos import member_repo, operator_repo, product_repo, order_repo, coupon_repo
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
            return render(request, 'home.html', {'member':member})

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
        result = {}
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

        return JsonResponse(result)

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

            result = {}
            return JsonResponse(result)
        return Response(status.HTTP_200_OK)