from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .repos import member_repo
# Create your views here.
class MemberViewSet(viewsets.ViewSet):
    # authentication_classes = ()
    # permission_classes = (permissions.AllowAny,)
    # renderer_classes = (TemplateHTMLRenderer,)

    @action(methods=['get'], detail=False, url_path='create')
    def create_member(self, request):
        member_repo.create('Bliss', 'Chen')
        return Response(status.HTTP_200_OK)
