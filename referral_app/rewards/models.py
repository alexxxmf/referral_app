from django.conf import settings
from django.db import models


class Reward(models.Model):
    db_table = 'rewards'

    title = models.CharField(max_length=40)
    description = models.CharField(max_length=255)
    image = models.ImageField()
    referrals_needed = models.IntegerField(default=1)
    live = models.BooleanField(default=True)

    # TODO: Prevent the user from adding more than one reward
    # with the same number of referrals needed.

    def __str__(self):
        return self.title

    def __repr__(self):
        return '<Reward: %s>' % (self.title)

    def save(self, *args, **kwargs):
        if self.referrals_needed == 0:
            raise Exception('Referrals needed should be greater than 0')
        reward = Reward.objects.filter(referrals_needed=self.referrals_needed).first()
        if reward:
            raise Exception('There is already a reward with the specified number of referrals needed')
        super(Reward, self).save(*args, **kwargs)

    def image_src(self):
        # ImageField inherits from FileField
        if self.image:
            return '<img src="%s" />' % self.image.url
        else:
            return '(No image)'

    image_src.short_description = 'Thumbnail'
    image_src.allow_tags = True
