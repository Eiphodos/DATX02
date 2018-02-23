from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from userdata.models import Userdata
from userdata.serializers import UserdataSerializer

import sys
sys.path.append(r"C:\Users\David\Documents\GitHub\DATX02\tensor")
import predict

import datetime

# Create your views here.
class UserdataViewSet(viewsets.ModelViewSet):
    # this fetches all the rows of data in the Userdata table
    queryset = Userdata.objects.all()
    serializer_class = UserdataSerializer

@csrf_exempt
def userdata_send(request):
    if request.method == 'GET':
        userdata = Userdata.objects.all()
        serializer = UserdataSerializer(userdata, many=True)
        return JsonResponse(serializer.data, safe=False)
    elif request.method == 'POST':
        data = JSONParser().parse(request)
        serializer = UserdataSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=201)
        return JsonResponse(serializer.errors, status=400)
    else:
        return JsonResponse(serializer.errors, status=405)

@csrf_exempt
def userdata_receive(request, userid):
    """
    Retrieve, update or delete a code snippet.
    """
    #try:
    #    userdata = Userdata.objects.get(userid=userid)
    #except Userdata.DoesNotExist:
    #    return HttpResponse(status=404)

    if request.method == 'GET':
        pulse = request.GET.get('heartrate')
        rating = 1.0
        timevalue = (((datetime.datetime.now().hour)*60) + datetime.datetime.now().minute)
        song = predict.predict(100, userid, float(pulse), float(timevalue), 1.0)
        data = Userdata.create(userid, song, pulse, rating)
        serializer = UserdataSerializer(data)
        return JsonResponse(song, safe=False)

    elif request.method == 'PUT':
        data = JSONParser().parse(request)
        serializer = UserdataSerializer(userdata, data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data)
        return JsonResponse(serializer.errors, status=400)

    elif request.method == 'DELETE':
        userdata.delete()
        return HttpResponse(status=204)