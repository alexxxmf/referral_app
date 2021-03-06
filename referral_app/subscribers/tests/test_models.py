from django.db.utils import IntegrityError
from django.test import TestCase

from subscribers.models import Subscriber


class TestSubscribersModel(TestCase):
    """
    Test suite for the subscriber model
    """
    def test_some_subscriber_fields(self):
        subscriber = Subscriber.objects.create(email='alex@test.com')
        self.assertEqual(subscriber.email, 'alex@test.com')
        self.assertEqual(str(subscriber), subscriber.email)
        self.assertNotEqual(len(subscriber.unique_code), 0)
        self.assertEqual(subscriber.unique_code[0:9], subscriber.password)

    def test_subscriber_default_fields_when_not_referred(self):
        subscriber = Subscriber.objects.create(email='alex@test.com')
        self.assertEqual(subscriber.confirmed_subscription, False)
        self.assertEqual(subscriber.referred, False)
        self.assertEqual(subscriber.referral_count, 0)

    def test_subscriber_model_in_db(self):
        subscriber_created = Subscriber.objects.create(
            email='alex@test.com',
            ip='127.0.0.0',
            referred=True,
            email_from_referrer='pepe@hotmail.com',
        )
        subscriber_pulled = Subscriber.objects.filter(
            email='alex@test.com'
        ).first()

        self.assertEqual(subscriber_created.email, subscriber_pulled.email)
        self.assertEqual(subscriber_pulled.ip, '127.0.0.0')
        self.assertEqual(subscriber_pulled.referred, True)
        self.assertEqual(
            subscriber_pulled.email_from_referrer,
            'pepe@hotmail.com'
        )

    def test_subscriber_email_unique(self):
        Subscriber.objects.create(email='alex@test.com')
        with self.assertRaises(IntegrityError):
            Subscriber.objects.create(email='alex@test.com')
