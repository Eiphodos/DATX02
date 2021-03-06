from userdata.models import Userdata
from rest_framework import serializers
import datetime

class UserdataSerializer(serializers.HyperlinkedModelSerializer):
    time = serializers.IntegerField(default=(((datetime.datetime.now().hour)*60) + datetime.datetime.now().minute))
    songssincelastplayed = serializers.IntegerField(required=False)
    ratingid = serializers.IntegerField(required=False)

    class Meta:
        model = Userdata
        fields = ('userid', 'songid', 'rating', 'heartrate', 'time', 'songssincelastplayed', 'ratingid')