from socket import gethostname, gethostbyname
import uuid

from django.db import models

# Create your models here.

class Subscriber(models.Model):
	db_table = 'subscribers'

	confirmed_subscription = models.BooleanField()
	email = models.EmailField(unique=True)
	email_from_referrer = models.EmailField(null=True, blank=True)
	ip = models.CharField(max_length=30)
	referral_count = models.IntegerField()
	referred = models.BooleanField()
	unique_code = models.CharField(max_length=120, unique=True)

	def save(self, referred=False, email_from_referrer=None,unique_code_provided=None, *args, **kwargs):
		self.confirmed_subscription = False
		self.ip = gethostbyname(gethostname())
		self.referred = referred
		self.email_from_referrer = email_from_referrer
		self.referral_count = 0
		self.unique_code = uuid.uuid4().hex
		
		super().save(*args, **kwargs)

	def __repr__(self):
		return '<Subscriber object %s>' %(self.email)

	def __str__(self):
		return self.email
