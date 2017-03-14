from django.db import models


class Reward(models.Model):
    title = models.CharField(max_length=40, default='')
    description = models.CharField(max_length=196, default='')
    image = models.CharField(max_length=196, default='')
    required_referrals = models.IntegerField(default=0)
    live = models.BooleanField(default=False)

    def __str__(self):
        return self.title

