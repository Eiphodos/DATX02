from django.db import models

import datetime

class Userdata(models.Model):
    userid = models.CharField(max_length=255)
    songid = models.CharField(max_length=255)
    heartrate = models.IntegerField()
    rating = models.FloatField()
    time = models.IntegerField(default=(((datetime.datetime.now().hour)*60) + datetime.datetime.now().minute))

    @classmethod
    def create(cls, userid, songid, heartrate, rating):
        userdata = cls(userid=userid, songid=songid, heartrate=heartrate, time=(((datetime.datetime.now().hour)*60) + datetime.datetime.now().minute), rating=rating)
        return userdata