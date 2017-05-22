from django.test import RequestFactory, TestCase


from subscribers.forms import (
    LoginForm,
    PasswordCreationForm,
    SubscriptionForm
)


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
