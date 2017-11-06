import uuid

from subscribers.utils import TooManySubscriptionsFromSameIP

from django.conf import settings
from django.db import models


# request.META.get('REMOTE_ADDR')
# TODO: use request.META to get ip from user. This is a dic so
# the important value would be this REMOTE_ADDR. The current method is going
# to give us the same ip all day long (server)
class Subscriber(models.Model):
    """
    Model to manage subscribers
    """
    db_table = 'subscribers'

    confirmed_subscription = models.BooleanField(default=False)
    email = models.EmailField(unique=True)
    email_from_referrer = models.EmailField(null=True, blank=True)
    ip = models.CharField(max_length=30)
    password = models.CharField(max_length=40)
    referral_count = models.IntegerField(default=0)
    referred = models.BooleanField(default=False)
    unique_code = models.CharField(max_length=120, unique=True)

    def save(self, *args, **kwargs):
        self.unique_code = uuid.uuid4().hex
        self.password = self.unique_code[0:9]
        subscribers_with_same_ip = Subscriber.objects.filter(ip=self.ip)
        # TODO: Is this a proper way to accomplish the task?
        LIMIT = settings.LIMIT_SUBSCRIBERS_FROM_SAME_IP
        if len(subscribers_with_same_ip) > LIMIT:
            raise TooManySubscriptionsFromSameIP

        super().save(*args, **kwargs)

    def __repr__(self):
        return '<Subscriber object %s>' % (self.email)

    def __str__(self):
        return self.email
