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
sys.path.append("/home/musik/DATX02/server/userdata/")
import Bucketizer

import datetime

recommendation_cache = {}
rid_cache = {}

# Bandits constant variables
numberofstates = 28
tempoactions = 10
modeactions = 2
loudnessactions = 7
timebuckets = 4
# Bandits
loudnessbandit = CBandit.CBandit(numberofstates, loudnessactions)
modebandit = CBandit.CBandit(numberofstates, modeactions)
tempobandit = CBandit.CBandit(numberofstates, tempoactions)



# Create your views here.
class UserdataViewSet(viewsets.ModelViewSet):
# this fetches all the rows of data in the Userdata table
    queryset = Userdata.objects.all()
    serializer_class = UserdataSerializer


# Method used to push data to the server with POST, at the moment used by all neural networks.
@csrf_exempt
def userdata_send(request):
    # Only used to view all data on the server for debugging at the moment
    if request.method == 'GET':
        userdata = Userdata.objects.all()
        serializer = UserdataSerializer(userdata, many=True)
        return JsonResponse(serializer.data, safe=False)
    elif request.method == 'POST':
        data = JSONParser().parse(request)
        serializer = UserdataSerializer(data=data)
        if serializer.is_valid():
            # Trackers for how long ago a song was last played by that user
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

# Method used by the first DNN setup to get recommendations from the server with GET
@csrf_exempt
def userdata_receive(request, userid):
    if request.method == 'GET':
        pulse = request.GET.get('heartrate')
        # Rating is set to 1 since we want a song with high rating
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
        # Update tracker for when the song was last played
        sc, created = SongCounter.objects.get_or_create(userid=userid, songid=song)
        delta = upc.playCounter - sc.lastPlayed
        # Send back the data to the client, it contains some extra information that we might strip later.
        data = Userdata.create(userid, song, pulse, rating, delta)
        serializer = UserdataSerializer(data)
        return JsonResponse(serializer.data, status=200)

    # Not used at the moment
    elif request.method == 'PUT':
        data = JSONParser().parse(request)
        serializer = UserdataSerializer(userdata, data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data)
        return JsonResponse(serializer.errors, status=400)

    # Not used at the moment
    elif request.method == 'DELETE':
        userdata.delete()
        return HttpResponse(status=204)

# Method used to get recommendations from the contextual bandit
@csrf_exempt
def userdata_receive_cbandit(request, userid):
    if request.method == 'GET':
        pulse = request.GET.get('heartrate')
        timevalue = (((datetime.datetime.now().hour) * 60) + datetime.datetime.now().minute)
        upc, created = UserPlayCounter.objects.get_or_create(userid=userid)
        # Only used since rating is a required value in our serializer
        rating = 1.0
        if ((userid in recommendation_cache) and recommendation_cache.get(userid)):
            song = recommendation_cache.get(userid).pop()
            # All songs that have been cached from one recommendation request will use the same ranking id
            rid = rid_cache.get(userid)
        else:
            usernumber = 0 #Placeholder, will be replaced by a userid lookup
            bucketedpulse = Bucketizer.bucketize_pulse(int(pulse))
            bucketedtime = Bucketizer.bucketize_time(timevalue)
            state = usernumber*numberofstates + bucketedpulse*timebuckets + bucketedtime
            # We get all ranking ids here but they will all be the same (since they are updated at the same time)
            # Might change this just to get one since its all we need.
            temporid, tempo = tempobandit.predict(state)
            moderid, mode = modebandit.predict(state)
            loudrid, loudness = loudnessbandit.predict(state)
            # Cache new songs based on bandit sugggestions
            recommendation_cache[userid] = ranking.ranking(Bucketizer.bucketize_tempo(tempo), Bucketizer.bucketize_loudness(loudness), mode, userid)
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

    # Not used at the moment
    elif request.method == 'PUT':
        data = JSONParser().parse(request)
        serializer = UserdataSerializer(userdata, data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data)
        return JsonResponse(serializer.errors, status=400)

    # Not used at the moment
    elif request.method == 'DELETE':
        userdata.delete()
        return HttpResponse(status=204)