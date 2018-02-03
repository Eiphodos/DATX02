from django.shortcuts import render

from rest_framework import viewsets
from rest_framework import permissions
from userdata.models import Userdata
from userdata.serializers import UserdataSerializer

# Create your views here.
class UserdataViewSet(viewsets.ModelViewSet):
    # this fetches all the rows of data in the Userdata table
    queryset = Userdata.objects.all()
    serializer_class = UserdataSerializer