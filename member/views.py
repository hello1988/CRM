from django.shortcuts import render
from django.http import JsonResponse
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth.mixins import LoginRequiredMixin
from rest_framework.authentication import BasicAuthentication, TokenAuthentication
from .repos import member_repo, operator_repo, product_repo, order_repo
# Create your views here.
class MemberViewSet(LoginRequiredMixin, viewsets.ViewSet):
    # authentication_classes = ()
    permission_classes = (permissions.IsAuthenticated,)
    # renderer_classes = (TemplateHTMLRenderer,)
    login_url = '/oauth/login/line'

    @action(methods=['get', 'post'], detail=False, url_path='home')
    def home(self, request):
        member = member_repo.get_by_user(request.user)
        if request.method == 'GET':
            if not member.registered:
                return render(request, 'registered.html', {})

            else:
                return render(request, 'home.html', {'member':member})

        elif request.method == 'POST':
            data = request.POST.dict()
            if not all(key in data for key in ['first_name', 'last_name', 'phone']):
                return render(request, 'registered.html', {})

            member.first_name = data['first_name']
            member.last_name = data['last_name']
            member.phone = data['phone']
            member.email = data.get('email', '')

            birth = data.get('birth', '')
            if birth.count('/') == 2:
                year, month, day = birth.split('/')
                member.birth_year = year
                member.birth_month = month
                member.birth_day = day

            member.registered = True
            member.save()
            return render(request, 'home.html', {'member':member})

        return Response(status.HTTP_200_OK)

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
            return render(request, 'checkout.html', {'member':member, 'products':products})

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