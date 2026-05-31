from django.db import models
from django.contrib.auth.models import User

class WeeklyLeaderboard(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    week_start = models.DateField()
    week_end = models.DateField()
    yentroww_count = models.IntegerField(default=0)
    rank = models.IntegerField(null=True, blank=True)
    reward_announced = models.BooleanField(default=False)
