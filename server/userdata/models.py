from django.db import models

class Userdata(models.Model):
    userid = models.IntegerField()
    songid = models.IntegerField()
    heartrate = models.IntegerField()
    time = models.DateTimeField('auto_now_add=True')
