from datetime import datetime
from email.policy import default
from django.db import models

from django.contrib.auth.models import User

# Create your models here.


class Board(models.Model):
    # writer = models.CharField(null=False, max_length=50)
    writer = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(null=False, max_length=200)
    content = models.TextField(null=False)
    hit = models.IntegerField(default=0)
    post_date = models.DateTimeField(default=datetime.now, blank=True)
    filename = models.CharField(null=False, max_length=500,
                                blank=True, default='')
    filesize = models.IntegerField(default=0)
    down = models.IntegerField(default=0)

    def hit_up(self):
        self.hit += 1

    def down_up(self):
        self.down += 1


class Comment(models.Model):
    # CASCADE : 외래키를 받아오는 테이블이 삭제될 때 외래키로 받는 테이블도 삭제
    board = models.ForeignKey(Board, on_delete=models.CASCADE)
    # writer = models.CharField(null=False, max_length=50)
    writer = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField(null=False)
    post_date = models.DateTimeField(default=datetime.now, blank=True)


class Forecast(models.Model):
    city = models.CharField(null=False, max_length=500)
    tmef = models.TextField(null=True)
    wf = models.TextField(null=True)
    tmn = models.IntegerField(default=0)
    tmx = models.IntegerField(default=0)


class Webtoon(models.Model):
    webDay = models.CharField(null=False, max_length=500, default='')
    title = models.TextField(null=True)
    writer = models.TextField(null=True)
    score = models.FloatField(default=0)
