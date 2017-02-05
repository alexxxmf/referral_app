from socket import gethostname, gethostbyname
from unittest import mock

from django.core.urlresolvers import reverse
from django.db.utils import IntegrityError
from django.http import HttpResponse
from django.test import TestCase, Client

from subscribers.views import HomeView
from subscribers.models import Subscriber
#from subscribers.models import Subscriber
#IntegrityError

client = Client()

#Views tests
class TestSubscribersViews(TestCase):

    def test_home_view_200_response(self):
        response = self.client.get(reverse('home'), follow=True)
        self.assertEqual(response.status_code, 200)
        response = self.client.post(reverse('home'), follow=True)
        self.assertEqual(response.status_code, 200)

#Models tests
class TestSubscribersModels(TestCase):
    def test_some_subscriber_fields(self):
        subscriber = Subscriber.objects.create(email='alex@test.com')
        current_ip = gethostbyname(gethostname())

        self.assertEqual(subscriber.email, 'alex@test.com')
        self.assertEqual(str(subscriber), subscriber.email)
        self.assertEqual(subscriber.ip, current_ip)
        self.assertNotEqual(len(subscriber.unique_code), 0)

    def test_subscriber_default_fields_when_not_referred(self):
        subscriber = Subscriber.objects.create(email='alex@test.com')
        self.assertEqual(subscriber.confirmed_subscription, False)
        self.assertEqual(subscriber.referred, False)
        self.assertEqual(subscriber.referral_count, 0)

    def test_subscriber_model_in_db(self):
        subscriber_created = Subscriber.objects.create(email='alex@test.com')
        subscriber_pulled = Subscriber.objects.filter(email='alex@test.com').first()
        self.assertEqual(subscriber_created.email, subscriber_pulled.email)

    def test_subscriber_email_unique(self):
        subscriber_created_1 = Subscriber.objects.create(email='alex@test.com')
        with self.assertRaises(IntegrityError):
            subscriber_created_2 = Subscriber.objects.create(email='alex@test.com')


	