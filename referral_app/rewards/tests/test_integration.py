import tempfile

from bs4 import BeautifulSoup

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from rewards.models import Reward
from subscribers.models import Subscriber


image_path = tempfile.NamedTemporaryFile(suffix=".jpg").name


class TestRewards(TestCase):

    def test_just_live_rewards_are_shown_in_dashboard(self):
        reward_1 = Reward.objects.create(
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
            referrals_needed=5,
            live=True
        )

        reward_2 = Reward.objects.create(
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
            referrals_needed=15,
            live=True
        )

        reward_3 = Reward.objects.create(
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
            referrals_needed=12,
            live=False
        )

        subscriber = Subscriber.objects.create(
            email='z@hot.com',
            confirmed_subscription=True,
            referral_count=2,
        )

        response_get = self.client.get(
            reverse(
                'dashboard',
                kwargs={'ref_code': subscriber.unique_code}
            )
        )

        soup = BeautifulSoup(response_get.content, "html.parser")
        html_content = soup.find_all(
            "li",
            attrs={
                "class": "reward",
            }
        )

        self.assertEqual(len(html_content), 2)
        list_from_html_content = [e.text.strip() for e in html_content]

        assert(
            reward_1.title and
            reward_1.title
            in list_from_html_content
        )

    def test_rewards_restrictions_for_referrals_needed(self):
        reward_1 = Reward.objects.create(
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
            referrals_needed=5,
            live=True
        )

        with self.assertRaises(Exception):
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

        with self.assertRaises(Exception):
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
                referrals_needed=0,
                live=True
            )
