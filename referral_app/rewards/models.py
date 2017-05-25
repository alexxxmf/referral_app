from django.conf import settings
from django.db import models


class Reward(models.Model):
    db_table = 'rewards'

    title = models.CharField(max_length=40)
    description = models.CharField(max_length=255)
    image = models.ImageField()
    referrals_needed = models.IntegerField(default=0)
    live = models.BooleanField(default=True)

    def __str__(self):
        return self.title

    def __repr__(self):
        return '<Reward: %s>' % (self.title)

    def image_src(self):
        # ImageField inherits from FileField
        if self.image:
            return '<img src="%s" />' % self.image.url
        else:
            return '(No image)'

    image_src.short_description = 'Thumbnail'
    image_src.allow_tags = True
