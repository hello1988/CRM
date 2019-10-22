from django.shortcuts import render
from django.http import HttpResponse
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth.mixins import LoginRequiredMixin

from .repos import member_repo
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
            pass
        else:
            pass
        return Response(status.HTTP_200_OK)
