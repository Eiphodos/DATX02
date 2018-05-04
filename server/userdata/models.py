from django.db import models

import sys
sys.path.append("/home/musik/DATX02/scripts/")
import training_data

import psycopg2
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
    userindex = models.IntegerField(null=True, blank=True)

    @classmethod
    def create(cls, userid):
        conn = training_data.connect_database()
        cursor = conn.cursor()
        usernumber = get_number_of_users(cursor)
        upc = cls(userid=userid, playCounter=0, last_update=0, userindex=usernumber)
        return upc

    def get_number_of_users(self, cursor):
        try:
            cursor.execute("""SELECT * FROM userdata_userplaycounter;""")
        except Exception as e:
            print("Something went wrong when trying to SELECT")
            print(e)
        numberofusers = cursor.rowcount
        return numberofusers

class SongCounter(models.Model):
    userid = models.CharField(max_length=255)
    songid = models.CharField(max_length=255)
    lastPlayed = models.IntegerField(default=0)

    @classmethod
    def create(cls, userid, songid):
        sc = cls(userid=userid, songid=songid)
        return sc