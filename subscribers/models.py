from socket import gethostname, gethostbyname
import uuid

from django.db import models

#request.META.get('REMOTE_ADDR')
#TODO: use request.META to get ip from user. This is a dic so
#the important value would be this REMOTE_ADDR. The current method is going
#to give us the same ip all day long (server)
class Subscriber(models.Model):
	db_table = 'subscribers'

	confirmed_subscription = models.BooleanField(default=False)
	email = models.EmailField(unique=True)
	email_from_referrer = models.EmailField(null=True, blank=True)
	ip = models.CharField(max_length=30)
	referral_count = models.IntegerField(default=0)
	referred = models.BooleanField(default=False)
	unique_code = models.CharField(max_length=120, unique=True)

	def save(self, *args, **kwargs):
		self.unique_code = uuid.uuid4().hex

		super().save(*args, **kwargs)

	def __repr__(self):
		return '<Subscriber object %s>' %(self.email)

	def __str__(self):
		return self.email
