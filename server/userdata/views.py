from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from userdata.models import Userdata
from userdata.models import UserPlayCounter
from userdata.models import SongCounter

from userdata.serializers import UserdataSerializer

import sys
sys.path.append("/home/musik/DATX02/tensor/")
import predict

import datetime

reccomendation_cache = {}



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
            upc, created = UserPlayCounter.objects.get_or_create(userid=serializer.validated_data['userid'])
            sc, created = SongCounter.objects.get_or_create(userid=serializer.validated_data['userid'], songid=serializer.validated_data['songid'])
            serializer.validated_data['songssincelastplayed'] = upc.playCounter - sc.lastPlayed
            upc.playCounter += 1
            sc.lastPlayed = upc.playCounter
            upc.save()
            sc.save()
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
        batch_size = 100
        timevalue = (((datetime.datetime.now().hour)*60) + datetime.datetime.now().minute)
        ckpstate = predict.get_checkpoint_state()
        upc, created = UserPlayCounter.objects.get_or_create(userid=userid)
        if (upc.last_update == ckpstate and reccomendation_cache.has_key(userid)):
            song = reccomendation_cache.get(userid).pop()
        else:
            reccomendation_cache[userid] = predict.predict(batch_size, userid, float(pulse), float(timevalue), rating)
            song = reccomendation_cache.get(userid).pop()
            upc.last_update = ckpstate
        sc, created = SongCounter.objects.get_or_create(userid=userid, songid=song)
        delta = upc.playCounter - sc.lastPlayed
        data = Userdata.create(userid, song, pulse, rating, delta)
        serializer = UserdataSerializer(data)
        return JsonResponse(serializer.data, status=200)

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