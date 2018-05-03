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
import LRModel
import DNNModel
sys.path.append("/home/musik/DATX02/rec_alg/")
import ranking
sys.path.append("/home/musik/DATX02/server/userdata/")
import Bucketizer

import datetime

recommendation_cache = {}


##################################################################
# Bandit Variables #
##################################################################

cb_rid_cache = {}
cb_recommendation_cache = {}

# Bandit checkpoint paths
CB_LOUD_CKPT_PATH = "/home/musik/DATX02/tensor-v2/checkpoints/cbandit/loud"
CB_TEMPO_CKPT_PATH = "/home/musik/DATX02/tensor-v2/checkpoints/cbandit/tempo"
CB_MODE_CKPT_PATH = "/home/musik/DATX02/tensor-v2/checkpoints/cbandit/mode"
# Bandits constant variables
CB_NUMBER_OF_STATES = 28
CB_TEMPO_ACTIONS = 10
CB_MODE_ACTIONS = 2
CB_LOUD_ACTIONS = 7
CB_TIME_BUCKETS = 4

# Cbandit output types
cb_outputloud = Bucketizer.BucketType.LOUDNESS
cb_outputmode = Bucketizer.BucketType.MODE
cb_outputtempo = Bucketizer.BucketType.TEMPO

# Bandits
LoudBandit = CBandit.CBandit(CB_NUMBER_OF_STATES, CB_LOUD_ACTIONS, CB_LOUD_CKPT_PATH, cb_outputloud)
ModeBandit = CBandit.CBandit(CB_NUMBER_OF_STATES, CB_MODE_ACTIONS, CB_MODE_CKPT_PATH, cb_outputmode)
TempoBandit = CBandit.CBandit(CB_NUMBER_OF_STATES, CB_TEMPO_ACTIONS, CB_TEMPO_CKPT_PATH, cb_outputtempo)

# Cbandit checkpoint state tracker
CB_CKPTSTATE = TempoBandit.get_checkpoint_state()

##################################################################
# Linear Regression Variables #
##################################################################

lr_recommendation_cache = {}

# Linear regression checkpoint paths
LR_LOUD_CKPT_PATH = "/home/musik/DATX02/tensor-v2/checkpoints/linreg/loud"
LR_TEMPO_CKPT_PATH = "/home/musik/DATX02/tensor-v2/checkpoints/linreg/tempo"
LR_MODE_CKPT_PATH = "/home/musik/DATX02/tensor-v2/checkpoints/linreg/mode"

# Linear regression feature columns
#lr_loudftcol = LRModel.LRModel.create_bucketized_numeric_feature_column("loudness", [-8, -6, -4, -2, 0, 2, 5])
#lr_modeftcol = LRModel.LRModel.create_numeric_feature_column("mode")
#lr_tempoftcol = LRModel.LRModel.create_bucketized_numeric_feature_column("tempo", [30, 50, 70, 90, 110, 130, 150, 170, 190, 210])

# Linear regression output types
lr_outputloud = Bucketizer.BucketType.LOUDNESS
lr_outputmode = Bucketizer.BucketType.MODE
lr_outputtempo = Bucketizer.BucketType.TEMPO

# Linear regression estimators
LoudLinReg = LRModel.LRModel(LR_LOUD_CKPT_PATH, lr_outputloud)
ModeLinReg = LRModel.LRModel(LR_MODE_CKPT_PATH, lr_outputmode)
TempoLinReg = LRModel.LRModel(LR_TEMPO_CKPT_PATH, lr_outputtempo)

# Linear regression checkpoint state tracker
# All should be trained at the same time so checkpointstate will be the same for all estimators.
LR_CKPTSTATE = TempoLinReg.get_checkpoint_state()

##################################################################
# DNN Variables #
##################################################################

dnn_recommendation_cache = {}

# DNN checkpoint paths
DNN_LOUD_CKPT_PATH = "/home/musik/DATX02/tensor-v2/checkpoints/dnn/loud"
DNN_TEMPO_CKPT_PATH = "/home/musik/DATX02/tensor-v2/checkpoints/dnn/tempo"
DNN_MODE_CKPT_PATH = "/home/musik/DATX02/tensor-v2/checkpoints/dnn/mode"

# DNN feature columns
#dnn_loudftcol = DNNModel.DNNModel.create_bucketized_numeric_feature_column("loudness", [-8, -6, -4, -2, 0, 2, 5])
#dnn_modeftcol = DNNModel.DNNModel.create_numeric_feature_column("mode")
#dnn_tempoftcol = DNNModel.DNNModel.create_bucketized_numeric_feature_column("tempo", [30, 50, 70, 90, 110, 130, 150, 170, 190, 210])

# DNN output types
dnn_outputloud = Bucketizer.BucketType.LOUDNESS
dnn_outputmode = Bucketizer.BucketType.MODE
dnn_outputtempo = Bucketizer.BucketType.TEMPO

# DNN estimators
LoudDNN = DNNModel.DNNModel(DNN_LOUD_CKPT_PATH, dnn_outputloud)
ModeDNN = DNNModel.DNNModel(DNN_MODE_CKPT_PATH, dnn_outputmode)
TempoDNN = DNNModel.DNNModel(DNN_TEMPO_CKPT_PATH, dnn_outputtempo)

# DNN checkpoint state tracker
# All should be trained at the same time so checkpointstate will be the same for all estimators.
DNN_CKPTSTATE = TempoLinReg.get_checkpoint_state()


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
        return HttpResponse(status=403)

# Method used to get recommendations from the contextual bandit
@csrf_exempt
def userdata_receive_cbandit(request, userid):
    global LoudBandit
    global ModeBandit
    global TempoBandit
    global CB_CKPTSTATE
    if request.method == 'GET':
        pulse = request.GET.get('heartrate')
        timevalue = (((datetime.datetime.now().hour) * 60) + datetime.datetime.now().minute)
        upc, created = UserPlayCounter.objects.get_or_create(userid=userid)
        # Only used since rating is a required value in our serializer
        rating = 1.0
        if (CB_CKPTSTATE < TempoBandit.get_checkpoint_state()):
            TempoBandit = CBandit.CBandit(CB_NUMBER_OF_STATES, CB_TEMPO_ACTIONS, CB_TEMPO_CKPT_PATH)
            LoudBandit = CBandit.CBandit(CB_NUMBER_OF_STATES, CB_LOUD_ACTIONS, CB_LOUD_CKPT_PATH)
            ModeBandit = CBandit.CBandit(CB_NUMBER_OF_STATES, CB_MODE_ACTIONS, CB_MODE_CKPT_PATH)
            CB_CKPTSTATE = TempoBandit.get_checkpoint_state()
        if ((userid in cb_recommendation_cache) and cb_recommendation_cache.get(userid)):
            song = cb_recommendation_cache.get(userid).pop()
            # All songs that have been cached from one recommendation request will use the same ranking id
            rid = cb_rid_cache.get(userid)
        else:
            usernumber = upc.userindex
            bucketedpulse = Bucketizer.bucketize_pulse(int(pulse))
            bucketedtime = Bucketizer.bucketize_time(timevalue)
            state = usernumber*CB_NUMBER_OF_STATES + bucketedpulse*CB_TIME_BUCKETS + bucketedtime
            # We get all ranking ids here but they will all be the same (since they are updated at the same time)
            # Might change this just to get one since its all we need.
            temporid, tempo = TempoBandit.predict(state)
            moderid, mode = ModeBandit.predict(state)
            loudrid, loudness = LoudBandit.predict(state)
            # Cache new songs based on bandit sugggestions
            cb_recommendation_cache[userid] = ranking.ranking(Bucketizer.bucketize_tempo(tempo), Bucketizer.bucketize_loudness(loudness), mode, userid)
            #all rankingids should be identical so it doesnt matter which one we choose
            cb_rid_cache[userid] = loudrid
            rid = loudrid
            song = cb_recommendation_cache.get(userid).pop()
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
        return HttpResponse(status=403)

# Method used to get recommendations from linear regression
@csrf_exempt
def userdata_receive_linreg(request, userid):
    global LoudLinReg
    global ModeLinReg
    global TempoLinReg
    global LR_CKPTSTATE
    if request.method == 'GET':
        timevalue = (((datetime.datetime.now().hour) * 60) + datetime.datetime.now().minute)
        pulse = request.GET.get('heartrate')
        upc, created = UserPlayCounter.objects.get_or_create(userid=userid)
        # Rating is set to 1 since we want a song with high rating
        rating = 1.0
        if (LR_CKPTSTATE < TempoLinReg.get_checkpoint_state()):
            LoudLinReg = LRModel.LRModel(LR_LOUD_CKPT_PATH, lr_outputloud)
            ModeLinReg = LRModel.LRModel(LR_MODE_CKPT_PATH, lr_outputmode)
            TempoLinReg = LRModel.LRModel(LR_TEMPO_CKPT_PATH, lr_outputtempo)
            LR_CKPTSTATE = TempoLinReg.get_checkpoint_state()
        if ((userid in lr_recommendation_cache) and lr_recommendation_cache.get(userid)):
            song = lr_recommendation_cache.get(userid).pop()
        else:
            data = {'user_id': [userid], 'time': [timevalue], 'heart_rate': [int(pulse)], 'rating': [rating]}
            tempo = int(TempoLinReg.get_predict_class_id(data_matrix=data))
            mode = int(ModeLinReg.get_predict_class_id(data_matrix=data))
            loudness = int(LoudLinReg.get_predict_class_id(data_matrix=data))
            # Cache new songs based on linreg sugggestions
            lr_recommendation_cache[userid] = ranking.ranking(tempo, loudness, mode, userid)
            song = lr_recommendation_cache.get(userid).pop()
        sc, created = SongCounter.objects.get_or_create(userid=userid, songid=song)
        delta = upc.playCounter - sc.lastPlayed
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
        return HttpResponse(status=403)

# Method used to get recommendations from DNN
@csrf_exempt
def userdata_receive_dnn(request, userid):
    global LoudDNN
    global ModeDNN
    global TempoDNN
    global DNN_CKPTSTATE
    if request.method == 'GET':
        timevalue = (((datetime.datetime.now().hour) * 60) + datetime.datetime.now().minute)
        pulse = request.GET.get('heartrate')
        upc, created = UserPlayCounter.objects.get_or_create(userid=userid)
        # Rating is set to 1 since we want a song with high rating
        rating = 1.0
        if (DNN_CKPTSTATE < TempoDNN.get_checkpoint_state()):
            LoudDNN = DNNModel.DNNModel(DNN_LOUD_CKPT_PATH, dnn_outputloud)
            ModeDNN = DNNModel.DNNModel(DNN_MODE_CKPT_PATH, dnn_outputmode)
            TempoDNN = DNNModel.DNNModel(DNN_TEMPO_CKPT_PATH, dnn_outputtempo)
            DNN_CKPTSTATE = TempoDNN.get_checkpoint_state()
        if ((userid in dnn_recommendation_cache) and dnn_recommendation_cache.get(userid)):
            song = dnn_recommendation_cache.get(userid).pop()
        else:
            data = {'user_id':[userid],'time':[timevalue],'heart_rate':[int(pulse)],'rating':[rating]}
            tempo = Bucketizer.bucketize_tempo(int(TempoDNN.get_predict_class_id(data_matrix=data)))
            mode = Bucketizer.bucketize_mode(int(ModeDNN.get_predict_class_id(data_matrix=data)))
            loudness = Bucketizer.bucketize_loudness(int(LoudDNN.get_predict_class_id(data_matrix=data)))
            # Cache new songs based on DNN sugggestions
            dnn_recommendation_cache[userid] = ranking.ranking(tempo, loudness, mode, userid)
            song = dnn_recommendation_cache.get(userid).pop()
        sc, created = SongCounter.objects.get_or_create(userid=userid, songid=song)
        delta = upc.playCounter - sc.lastPlayed
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
        return HttpResponse(status=403)
