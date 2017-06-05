from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from rewards.models import Reward
from subscribers.utils import relative_progress
from subscribers.models import Subscriber

class TestRelativeProgress(TestCase):
    def test_relative_progress(self):

        subscriber_1 = Subscriber.objects.create(
            email='bb@hot.com',
            confirmed_subscription=True,
            referral_count=2,
        )
        rewards = Reward.objects.filter(live=True).all()

        width = relative_progress(subscriber_1, rewards)
        self.assertEqual(width, 0)

        Reward.objects.create(
            title='Reward 1',
            description='Random description',
            image=SimpleUploadedFile(
                name='test_image1.jpg',
                content=open(
                    settings.BASE_DIR + '/rewards/tests/random_picture.jpg',
                    'rb'
                ).read(),
                content_type='image/jpeg'
            ),
            referrals_needed=12,
            live=True
        )

        Reward.objects.create(
            title='Reward 2',
            description='Random description',
            image=SimpleUploadedFile(
                name='test_image2.jpg',
                content=open(
                    settings.BASE_DIR + '/rewards/tests/random_picture.jpg',
                    'rb'
                ).read(),
                content_type='image/jpeg'
            ),
            referrals_needed=5,
            live=True
        )

        Reward.objects.create(
            title='Reward 3',
            description='Random description',
            image=SimpleUploadedFile(
                name='test_image3.jpg',
                content=open(
                    settings.BASE_DIR + '/rewards/tests/random_picture.jpg',
                    'rb'
                ).read(),
                content_type='image/jpeg'
            ),
            referrals_needed=15,
            live=True
        )

        subscriber_2 = Subscriber.objects.create(
            email='z@hot.com',
            confirmed_subscription=True,
            referral_count=6,
        )

        subscriber_3 = Subscriber.objects.create(
            email='a@hot.com',
            confirmed_subscription=True,
            referral_count=0,
        )

        subscriber_4 = Subscriber.objects.create(
            email='b@hot.com',
            confirmed_subscription=True,
            referral_count=15,
        )

        rewards = Reward.objects.filter(live=True).all()

        width = relative_progress(subscriber_2, rewards)
        self.assertEqual(width, 45)

        width = relative_progress(subscriber_3, rewards)
        self.assertEqual(width, 25)

        width = relative_progress(subscriber_4, rewards)
        self.assertEqual(width, 100)
