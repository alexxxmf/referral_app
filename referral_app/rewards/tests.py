from django.test import TestCase

from rewards.models import Reward


class TestRewardsModel(TestCase):

    def test_reward_str(self):
        reward = Reward.objects.create(
            title='Sample 1',
            description='This is just a test',
            image='url-to-image',
            required_referrals=3,
            live=True

        )

        self.assertEqual(str(reward), reward.title)
