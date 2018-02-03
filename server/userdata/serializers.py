from userdata.models import Userdata
from rest_framework import serializers

class UserdataSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Userdata
        fields = ('userid', 'songid', 'heartrate', 'time')