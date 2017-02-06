from socket import gethostname, gethostbyname
from bs4 import BeautifulSoup

from django.core.urlresolvers import reverse
from django.db.utils import IntegrityError
from django.http import HttpResponse
from django.test import TestCase, Client

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
        form_html = soup.find(class_='form-inline')
        self.assertNotEqual(form_html, None)
        #check action value to see if posted content is being sent to the right url
        action_html_attribute = form_html.find(attrs={"action" : reverse('home')})
        self.fail(action_html_attribute)
        #check that method attribute is set to post

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

    def test_home_view_context(self):
        response = self.client.get(reverse('home'), follow=True)
        #check that 'form' exists in context
        self.assertTrue('form' in response.context)


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
