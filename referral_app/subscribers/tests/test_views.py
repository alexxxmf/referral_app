from django.test import RequestFactory, TestCase
from django.urls import reverse

from subscribers.models import Subscriber
from subscribers.views import (
    ConfirmationView,
    HomeView,
    MailChimpListenerView,
    DashboardView
)


class TestHomeView(TestCase):
    """
    Test suite for the home page
    """
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


class TestConfirmationView(TestCase):
    """
    Test suite for the confirmation page
    """
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


class TestDashboardView(TestCase):
    """
    Test suite for the dashboard page
    """
    def setUp(self):
        self.factory = RequestFactory()
        self.dashboard_view = DashboardView()

    def test_data_from_subscriber_shown(self):
        pass


class TestMailChimpListenerView(TestCase):
    """
    Test suite for the mailchimp page
    """
    def setUp(self):
        self.factory = RequestFactory()
        self.mc_listener_view = MailChimpListenerView()

    def test_mailchimplistener_view_does_not_accept_get_requests(self):
        pass

    def test_mailchimplistener_is_csrf_exempt(self):
        pass

    def test_referrer_count_updated(self):
        referrer_start_status = Subscriber.objects.create(
            email='a@hot.com'
        )
        Subscriber.objects.create(
            email='b@hot.com',
            referred=True,
            email_from_referrer='a@hot.com'
        )
        starting_count = referrer_start_status.referral_count
        data = {'data[email]': 'b@hot.com', 'type': 'subscribe'}
        post_request = self.factory.post(reverse('mailchimp_listener'), data)
        self.mc_listener_view.post(post_request)
        referrer_end_status = Subscriber.objects.filter(
            email='a@hot.com',
        ).first()

        subscriber_after_confirmation = Subscriber.objects.filter(
            email='b@hot.com'
        ).first()

        self.assertTrue(subscriber_after_confirmation.confirmed_subscription)
        self.assertEqual(starting_count, 0)
        self.assertEqual(referrer_end_status.referral_count, 1)
