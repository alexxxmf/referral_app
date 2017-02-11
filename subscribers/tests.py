from bs4 import BeautifulSoup
from unittest.mock import Mock, patch

from django.contrib.sessions.models import Session
from django.db.utils import IntegrityError
from django.http import HttpResponse
from django.test import Client, RequestFactory, TestCase
from django.urls import reverse

from subscribers.forms import LoginForm, SubscriptionForm, PasswordCreationForm
from subscribers.models import Subscriber
from subscribers.views import HomeView, LoginView, ConfirmationView

#Integration tests
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

    def test_subscriber_created_and_redirected_when_right_ref_code(self):
        #we have to check user is properly created and it's been properly redirected

        subscriber_1 = Subscriber.objects.create(email='abel@hot.com')
        #we have to create a session for the ref_code
        response_get = self.client.get(
            reverse('home') +
            '?ref_code=' +
            subscriber_1.unique_code,
        )
        #about storing sessions
        #http://stackoverflow.com/questions/4453764/how-do-i-modify-the-session-in-the-django-test-framework
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
            {'email':'a@hot.com'},
            HTTP_REMOTE_ADDR='127.0.0.1'
        )

        subscriber_2 = Subscriber.objects.filter(email='a@hot.com').first()
        self.assertNotEqual(subscriber_2, None)
        self.assertTrue(subscriber_2.referred, True)
        self.assertEqual(subscriber_2.email_from_referrer, 'abel@hot.com')
        self.assertEqual(response_post.url, reverse('confirmation_prompt'))
    #in tests not working but working properly when running server
    #wtf is happening??!!!
    def test_subscriber_already_in_db_without_confirmation(self):
        subscriber = Subscriber.objects.create(email='a@hot.com')

        response_post = self.client.post(
            reverse('home'),
            {'email':'b@hot.com'},
            HTTP_REMOTE_ADDR='127.0.0.1'
        )

        self.assertEqual(response_post.url, reverse('confirmation_prompt'))

    def test_subscriber_already_in_db_with_confirmation(self):
        subscriber = Subscriber.objects.create(email='b@hot.com')
        subscriber.confirmed_subscription = True
        subscriber.save()

        response_post = self.client.post(
            reverse('home'),
            {'email':'b@hot.com'},
            HTTP_REMOTE_ADDR='127.0.0.1'
        )

        self.assertEqual(response_post.url, reverse('login'))


#Templates tests
class TestHomeTemplate(TestCase):

    def test_home_template_title(self):
        response = self.client.get(reverse('home'), follow=True)
        self.assertNotEqual(response.content.find(b'<title>Home</title>'), -1)

    def test_home_template_form_rendered_properly(self):
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

class TestLoginTemplate(TestCase):

    def test_login_template_title(self):
        response = self.client.get(reverse('login'), follow=True)
        self.assertNotEqual(response.content.find(b'<title>Login</title>'), -1)

    def test_login_template_form_rendered_properly(self):
        response = self.client.get(reverse('login'), follow=True)
        soup = BeautifulSoup(response.content, 'html.parser')

        form_html_attr = soup.find(
            'form',
            attrs={
                "action": reverse('login'),
                "method": 'post',
                "role": 'form',
            }
        )
        self.assertNotEqual(form_html_attr, None)
        email_input_attr = soup.find(
            'input',
            attrs={
                "maxlength": '100',
                "name": 'email',
                "type": 'email',
            }
        )
        self.assertNotEqual(email_input_attr, None)
        password_input_attr = soup.find(
            'input',
            attrs={
                "name": 'password',
                "type": 'password',
            }
        )
        self.assertNotEqual(password_input_attr, None)
        submit_btn_attr = soup.find(
            'input',
            attrs={
                "type": 'submit',
                "value": 'Submit',
            }
        )
        self.assertNotEqual(submit_btn_attr, None)

class TestConfirmationTemplate(TestCase):

    def test_confirmation_template_content_rendered_properly(self):
        response = self.client.get(reverse('confirmation_prompt'), follow=True)
        soup = BeautifulSoup(response.content, 'html.parser')
        main_prompt = soup.find(
            'h1',
            attrs={
                "id": 'main_confirmation_prompt',
            }
        )
        self.assertNotEqual(main_prompt, None)

#Forms tests
class TestSubscriptionForm(TestCase):

    def test_form_validates_email(self):
        data = {'email': 'blabla'}
        form = SubscriptionForm(data)
        self.assertEqual(form.is_valid(), False)
        data = {'email': 'alex@blabla.com'}
        form = SubscriptionForm(data)
        self.assertEqual(form.is_valid(), True)

class TestLoginForm(TestCase):

    def test_form_validates_email(self):
        data = {'email': 'blabla', 'password': 'blabla'}
        form = LoginForm(data)
        self.assertEqual(form.is_valid(), False)
        data = {'email': 'alex@blabla.com', 'password': 'blabla'}
        form = LoginForm(data)
        self.assertEqual(form.is_valid(), True)

class TestPasswordCreationForm(TestCase):

    def test_form_validates_password(self):
        data = {'email': 'blabla', 'password': 'blabla'}
        form = PasswordCreationForm(data)
        self.assertEqual(form.is_valid(), False)

#Views tests
class TestHomeView(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.home_view = HomeView()

    def test_home_view_200_response(self):
        get_request = self.factory.get(reverse('home'))
        response = self.home_view.get(get_request)
        self.assertEqual(response.status_code, 200)

        post_request = self.factory.post(reverse('home'))
        response = self.home_view.post(post_request)
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

class TestLoginView(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.login_view = LoginView()

    def test_home_view_200_response(self):
        get_request = self.factory.get(reverse('login'))
        response = self.login_view.get(get_request)
        self.assertEqual(response.status_code, 200)

    def test_login_view_loads_right_template(self):
        response = self.client.get(reverse('login'), follow=True)
        self.assertTemplateUsed(response, 'subscribers/login.html')
        self.assertTemplateUsed(response, 'base.html')

    def test_home_view_context_with_post_request(self):
        response = self.client.get(reverse('home'), follow=True)
        self.assertTrue('form' in response.context)

class TestConfirmationView(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.confirmation_view = ConfirmationView()

    def test_confirmation_view_200_response(self):
        get_request = self.factory.get(reverse('confirmation_prompt'))
        response = self.confirmation_view.get(get_request)
        self.assertEqual(response.status_code, 200)

    def test_confirmation_view_loads_right_template(self):
        response = self.client.get(reverse('confirmation_prompt'), follow=True)
        self.assertTemplateUsed(response, 'subscribers/confirmation.html')
        self.assertTemplateUsed(response, 'base.html')

class TestMailChimpListenerView(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_confirmation_view_does_not_accept_get_requests(self):
        get_request = self.factory.get(reverse('mailchimp_listener'))
        response = self.confirmation_view.get(get_request)
        self.assertEqual(response.status_code, 200)


#Remember to apply DRy and create a class that inherits from TestCase with 
#RequestFactory within factory attr and make all view testcases inherit from it
class TestCreatePassword(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.confirmation_view = ConfirmationView()

    def test_createpassword_view_200_response(self):
        get_request = self.factory.get(reverse('create_password'))
        response = self.confirmation_view.get(get_request)
        self.assertEqual(response.status_code, 200)

    def test_createpassword_view_loads_right_template(self):
        response = self.client.get(reverse('create_password'), follow=True)
        self.assertTemplateUsed(response, 'subscribers/create_password.html')
        self.assertTemplateUsed(response, 'base.html')

    def test_home_view_context_with_post_request(self):
        response = self.client.get(reverse('create_password'), follow=True)
        self.assertTrue('form' in response.context)

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
