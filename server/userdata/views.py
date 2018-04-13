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
sys.path.append("/home/musik/DATX02/tensor-v2/")
import CBandit
sys.path.append("/home/musik/DATX02/rec_alg/")
import ranking
import Bucketizer

import datetime

recommendation_cache = {}
rid_cache = {}

# Bandits constant variables
numberofstates = 20
tempoactions = 5
modeactions = 2
loudnessactions = 5
# Bandits
loudnessbandit = CBandit.CBandit(numberofstates, loudnessactions)
modebandit = CBandit.CBandit(numberofstates, modeactions)
tempobandit = CBandit.CBandit(numberofstates, tempoactions)



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
        if (upc.last_update == ckpstate and (userid in recommendation_cache)):
            song = recommendation_cache.get(userid).pop()
        else:
            recommendation_cache[userid] = predict.predict(batch_size, userid, float(pulse), float(timevalue), rating)
            song = recommendation_cache.get(userid).pop()
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

@csrf_exempt
def userdata_receive_cbandit(request, userid):
    """
    Retrieve, update or delete a code snippet.
    """
    # try:
    #    userdata = Userdata.objects.get(userid=userid)
    # except Userdata.DoesNotExist:
    #    return HttpResponse(status=404)

    if request.method == 'GET':
        pulse = request.GET.get('heartrate')
        timevalue = (((datetime.datetime.now().hour) * 60) + datetime.datetime.now().minute)
        upc, created = UserPlayCounter.objects.get_or_create(userid=userid)
        rating = 1.0
        if ((userid in recommendation_cache) and recommendation_cache.get(userid)):
            song = recommendation_cache.get(userid).pop()
            rid = rid_cache.get(userid)
        else:
            usernumber = 0 #Placeholder
            bucketedpulse = Bucketizer.bucketize_pulse(pulse)
            bucketedtime = Bucketizer.bucketize_time(timevalue)
            state = usernumber*numberofstates + bucketedpulse
            temporid, tempo = tempobandit.predict(state)
            moderid, mode = modebandit.predict(state)
            loudrid, loudness = loudnessbandit.predict(state)
            recommendation_cache[userid] = ranking.ranking(Buckertizer.bucketize_tempo(tempo), Buckertizer.bucketize_loudness(loudness), mode, userid)
            #all rankingids should be identical so it doesnt matter which one we choose
            rid_cache[userid] = loudrid
            rid = loudrid
            song = recommendation_cache.get(userid).pop()
        sc, created = SongCounter.objects.get_or_create(userid=userid, songid=song)
        delta = upc.playCounter - sc.lastPlayed
        data = Userdata.create(userid, song, pulse, rating, delta)
        data.ratingid = rid
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