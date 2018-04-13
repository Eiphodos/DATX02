from django.db import models

import datetime

class Userdata(models.Model):
    userid = models.CharField(max_length=255)
    songid = models.CharField(max_length=255)
    heartrate = models.IntegerField()
    rating = models.FloatField()
    time = models.IntegerField(default=(((datetime.datetime.now().hour)*60) + datetime.datetime.now().minute))
    songssincelastplayed = models.IntegerField(null=True, blank=True)
    ratingid = models.IntegerField(null=True, blank=True)

    @classmethod
    def create(cls, userid, songid, heartrate, rating, sslp):
        userdata = cls(userid=userid, songid=songid, heartrate=heartrate, time=(((datetime.datetime.now().hour)*60) + datetime.datetime.now().minute), rating=rating, songssincelastplayed = sslp)
        return userdata

class UserPlayCounter(models.Model):
    userid = models.CharField(max_length=255)
    playCounter = models.IntegerField(default=0)
    last_update = models.IntegerField(default=0, blank=True)

    @classmethod
    def create(cls, userid):
        upc = cls(userid=userid, playCounter=0, last_update=0)
        return upc

class SongCounter(models.Model):
    userid = models.CharField(max_length=255)
    songid = models.CharField(max_length=255)
    lastPlayed = models.IntegerField(default=99999)

    @classmethod
    def create(cls, userid, songid):
        sc = cls(userid=userid, songid=songid)
        return sc