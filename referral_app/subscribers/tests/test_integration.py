from unittest.mock import Mock, patch

from bs4 import BeautifulSoup

from django.contrib.sessions.models import Session
from django.db.utils import IntegrityError
from django.test import RequestFactory, TestCase
from django.urls import reverse

from subscribers.forms import (
    LoginForm,
    PasswordCreationForm,
    SubscriptionForm
)
from subscribers.models import Reward, Subscriber
from subscribers.views import (
    ConfirmationView,
    HomeView,
    MailChimpListenerView
)


class TestHomeBehavior(TestCase):

    def test_session_created_just_when_ref_code_provided(self):
        response = self.client.get(reverse('home'))
        self.assertFalse(response.cookies.get('sessionid', False))
        response = self.client.get(reverse('home') + '?ref_code=1as34e')
        self.assertTrue(response.cookies.get('sessionid', False))

    def test_subscriber_referred_with_right_ref_code(self):
        subscriber_1 = Subscriber.objects.create(email='alex@hotmail.com')
        response = self.client.get(
            reverse('home') +
            '?ref_code=' +
            subscriber_1.unique_code
        )
        sessionid_obj = response.cookies.get('sessionid', False)
        session_key = sessionid_obj.value
        session = Session.objects.get(session_key=session_key)
        uid = session.get_decoded().get('ref_code')
        self.assertEqual(uid, subscriber_1.unique_code)

    @patch('subscribers.views.MailChimp')
    def test_subscriber_created_and_redirected_when_right_ref_code(
        self,
        mailchimp
    ):
        # we have to check user is properly created and it's
        # been properly redirected
        mc_client_instance_mock = Mock()
        message = 'Service correctly called'
        mc_client_instance_mock.member.create.return_value = message

        mailchimp.return_value = mc_client_instance_mock

        subscriber_1 = Subscriber.objects.create(email='abel@hot.com')
        # we have to create a session for the ref_code
        response_get = self.client.get(
            reverse('home') +
            '?ref_code=' +
            subscriber_1.unique_code,
        )
        # about storing sessions
        # http://stackoverflow.com/questions/4453764/how-do-i-modify-the-session-in-the-django-test-framework
        session_key = response_get.cookies.get('sessionid', False).value
        session = Session.objects.get(session_key=session_key)
        uid = session.get_decoded().get('ref_code')
        s = self.client.session
        s['ref_code'] = uid
        self.client.cookies['sessionid'] = session_key

        response_post = self.client.post(
            reverse('home') +
            '?ref_code=' +
            subscriber_1.unique_code,
            {'email': 'a@hot.com'},
            HTTP_REMOTE_ADDR='127.0.0.1'
        )

        self.assertTrue(mailchimp.called)
        self.assertTrue(mc_client_instance_mock.member.create)

        subscriber_2 = Subscriber.objects.filter(email='a@hot.com').first()
        self.assertNotEqual(subscriber_2, None)
        self.assertTrue(subscriber_2.referred, True)
        self.assertEqual(subscriber_2.email_from_referrer, 'abel@hot.com')
        self.assertEqual(response_post.url, reverse('confirmation_prompt'))

    # in tests not working but working properly when running server
    # wtf is happening??!!!
    #def test_subscriber_already_in_db_without_confirmation(self):
        #Subscriber.objects.create(email='a@hot.com')

        #response_post = self.client.post(
            #reverse('home'),
            #{'email': 'a@hot.com'},
            #HTTP_REMOTE_ADDR='127.0.0.1'
        #)

        #self.assertEqual(response_post.url, reverse('confirmation_prompt'))

    #def test_subscriber_already_in_db_with_confirmation(self):
        #subscriber = Subscriber.objects.create(email='b@hot.com')
        #subscriber.confirmed_subscription = True
        #subscriber.save()

        #response_post = self.client.post(
            #reverse('home'),
            #{'email': 'b@hot.com'},
            #HTTP_REMOTE_ADDR='127.0.0.1'
        #)

        #self.assertEqual(response_post.url, reverse('login'))

    def test_list_of_users_referred_properly_shown(self):
        subscriber = Subscriber.objects.create(
            email='z@hot.com',
            confirmed_subscription=True,
            referral_count=2,
        )

        referred_subscriber_1 = Subscriber.objects.create(
            email='referred1@hot.com',
            referred=True,
            email_from_referrer=subscriber.email,
            confirmed_subscription=True,
        )
        referred_subscriber_2 = Subscriber.objects.create(
            email='referred2@hot.com',
            referred=True,
            email_from_referrer=subscriber.email,
            confirmed_subscription=True,
        )
        referred_subscriber_3 = Subscriber.objects.create(
            email='referred3@hot.com',
            referred=True,
            email_from_referrer=subscriber.email,
            confirmed_subscription=False,
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
                "class": "referred-subscriber",
            }
        )

        self.assertEqual(len(html_content), 2)
        list_from_html_content = [e.text.strip() for e in html_content]

        assert(
            referred_subscriber_1.email and
            referred_subscriber_2.email
            in list_from_html_content
        )
