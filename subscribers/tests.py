from bs4 import BeautifulSoup

from django.core.urlresolvers import reverse
from django.db.utils import IntegrityError
from django.http import HttpResponse
from django.test import Client, RequestFactory, TestCase

from subscribers.forms import SubscriptionForm
from subscribers.models import Subscriber
from subscribers.views import HomeView


#Templates tests
class TestSubscribersTemplates(TestCase):

    def test_home_view_title(self):
        response = self.client.get(reverse('home'), follow=True)
        self.assertNotEqual(response.content.find(b'<title>Home</title>'), -1)

    def test_home_view_form_rendered_properly(self):
        response = self.client.get(reverse('home'), follow=True)
        soup = BeautifulSoup(response.content, 'html.parser')

        form_html_attr = soup.find(
            'form',
            attrs={
                "action": reverse('home'),
                "method": 'post',
                "role": 'form',
            })
        self.assertNotEqual(form_html_attr, None)
        email_input_attr = soup.find(
            'input',
            attrs={
                "maxlength": '100',
                "name": 'email',
                "type": 'email',
            })
        self.assertNotEqual(email_input_attr, None)
        submit_btn_attr = soup.find(
            'input',
            attrs={
                "type": 'submit',
                "value": 'Submit',
            })
        self.assertNotEqual(submit_btn_attr, None)

#Forms tests
class TestSubscribersForms(TestCase):

    def test_form_validates_email(self):
        data = {'email': 'blabla'}
        form = SubscriptionForm(data)
        self.assertEqual(form.is_valid(), False)
        data = {'email': 'alex@blabla.com'}
        form = SubscriptionForm(data)
        self.assertEqual(form.is_valid(), True)

#Views tests
class TestSubscribersViews(TestCase):

    def test_home_view_200_response(self):
        response = self.client.get(reverse('home'), follow=True)
        self.assertEqual(response.status_code, 200)
        response = self.client.post(reverse('home'), follow=True)
        self.assertEqual(response.status_code, 200)

    def test_home_view_loads_right_template(self):
        response = self.client.get(reverse('home'), follow=True)
        self.assertTemplateUsed(response, 'subscribers/home.html')
        self.assertTemplateUsed(response, 'base.html')

    def test_home_view_context_with_get_request(self):
        response = self.client.get(reverse('home'), follow=True)
        self.assertTrue('form' in response.context)

    def test_home_view_context_with_post_request(self):
        response = self.client.post(reverse('home'), follow=True)
        self.assertTrue('form' in response.context)

    def test_form_in_post_request_properly_gets_posted_values(self):
        request_factory = RequestFactory()
        post_data = {
            "email": "alex@hotmail.com",
        }
        request = request_factory.post(reverse('home'), form=post_data)
        #home = HomeView()
        #home(request)

#Models tests
class TestSubscribersModels(TestCase):
    def test_some_subscriber_fields(self):
        subscriber = Subscriber.objects.create(email='alex@test.com')
        self.assertEqual(subscriber.email, 'alex@test.com')
        self.assertEqual(str(subscriber), subscriber.email)

    def test_subscriber_default_fields_when_not_referred(self):
        subscriber = Subscriber.objects.create(email='alex@test.com')
        self.assertEqual(subscriber.confirmed_subscription, False)
        self.assertEqual(subscriber.referred, False)
        self.assertEqual(subscriber.referral_count, 0)
        self.assertNotEqual(len(subscriber.unique_code), 0)

    def test_subscriber_model_in_db(self):
        subscriber_created = Subscriber.objects.create(
            email='alex@test.com',
            ip='127.0.0.0',
            referred=True,
            email_from_referrer='pepe@hotmail.com',
        )
        subscriber_pulled = Subscriber.objects.filter(email='alex@test.com').first()
        self.assertEqual(subscriber_created.email, subscriber_pulled.email)
        self.assertEqual(subscriber_pulled.ip, '127.0.0.0')
        self.assertEqual(subscriber_pulled.referred, True)
        self.assertEqual(subscriber_pulled.email_from_referrer, 'pepe@hotmail.com')

    def test_subscriber_email_unique(self):
        subscriber_created_1 = Subscriber.objects.create(email='alex@test.com')
        with self.assertRaises(IntegrityError):
            subscriber_created_2 = Subscriber.objects.create(email='alex@test.com')
