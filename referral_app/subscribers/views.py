from braces.views import CsrfExemptMixin

from django.db.models import F
from django.http import HttpResponse
# HttpResponseBadRequest
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.generic import TemplateView


from mailchimp3 import MailChimp

from referral_app.settings import (
    MAILCHIMP_API_KEY,
    MAILCHIMP_USERNAME,
    SUBSCRIBERS_LIST_ID
)

from subscribers.forms import LoginForm, PasswordCreationForm, SubscriptionForm
from subscribers.models import Subscriber


class HomeView(TemplateView):
    """
    CBV for the main page with the email form
    """
    template_name = 'home.html'

    def get(self, request, ref_code=None):
        """
        Function to manage the normal GET request
        """
        form = SubscriptionForm()
        ref_code = request.GET.get('ref_code', None)
        context = {
            'form': form,
        }
        if ref_code:
            request.session['ref_code'] = ref_code

        return render(
            request,
            'subscribers/home.html',
            context
        )

    # Check if it is compulsory to set a default for ref_code as in Flask
    def post(self, request, ref_code=None):
        """
        Function to manage email submitted via POST from email input form
        """
        mc_client = MailChimp(MAILCHIMP_USERNAME, MAILCHIMP_API_KEY)
        form = SubscriptionForm(request.POST)
        # if valid ref code means it's referred by someone
        if form.is_valid():
            email = form.cleaned_data['email']
            ip_from_user = request.META.get('REMOTE_ADDR', '0')

            if request.session.get('ref_code', False):
                email_from_referrer = Subscriber.objects.filter(
                    unique_code=request.session['ref_code']
                ).first()
                if email_from_referrer:
                    referred = True
                else:
                    referred = False
            else:
                email_from_referrer = None
                referred = False

            subscriber, created = Subscriber.objects.get_or_create(
                email=email,
                defaults={
                    'ip': ip_from_user,
                    'email_from_referrer': email_from_referrer,
                    'referred': referred,
                },
            )
            # better to force confirmation to update referral count
            subscriber = Subscriber.objects.filter(email=email).first()
            # should I add here a context depending if the user is created or
            # not but w/o confirmation
            if created:
                mc_client.member.create(
                    SUBSCRIBERS_LIST_ID, {
                        'email_address': email,
                        'status': 'pending'
                    }
                )

                return redirect(reverse('confirmation_prompt'))

            elif subscriber.confirmed_subscription is False:
                return redirect(reverse('confirmation_prompt'))

            else:
                return redirect(reverse('login'))

        context = {
            'form': form,
        }
        return render(
            request,
            'subscribers/home.html',
            context
        )



class ConfirmationView(TemplateView):
    """
    CBV for the page to remind the user to confirm email sub.
    """
    template_name = 'confirmation.html'

    def get(self, request):
        """
        Function to manage normal GET request
        """
        context = {}

        return render(
            request,
            'subscribers/confirmation.html',
            context
        )


class MailChimpListenerView(CsrfExemptMixin, TemplateView):
    """
    CBV for the MailChimp Listener. Here we receive data back from ML like
    for example when we got a new sub. Here is how it's being managed.
    """
    def get(self, request):
        """
        Function to manage normal GET request. It's declared but it's meant to
        not be used at all.
        """
        r = HttpResponse('Method not allowed', status=400)
        return r

    # data from POST is a QueryDict
    def post(self, request):
        """
        Function to manage normal POST request. Here is the way we store all
        the data sent by ML.
        """
        mailchimp_subs_data = request.POST.dict()
        if mailchimp_subs_data['type'] == 'subscribe':
            email = mailchimp_subs_data['data[email]']
            subscriber = Subscriber.objects.filter(email=email).first()
            subscriber.confirmed_subscription = True
            subscriber.save()

            if subscriber.referred:
                Subscriber.objects.filter(
                    email=subscriber.email_from_referrer
                ).update(
                    referral_count=F('referral_count') + 1
                )

        return HttpResponse('ok')


class DashboardView(CsrfExemptMixin, TemplateView):
    """
    CBV to present all the data to the user.
    """
    def get(self, request, ref_code):
        subscriber = Subscriber.objects.filter(unique_code=ref_code).first()

        if subscriber:
            has_referred_somebody = False
            referred_people = Subscriber.objects.filter(
                email_from_referrer=subscriber.email,
                confirmed_subscription=True
            )
            if len(referred_people) >= 1:
                has_referred_somebody = True

            context = {
                'ref_code': ref_code,
                'subscriber': subscriber,
                'referred_people': referred_people,
                'has_referred_somebody': has_referred_somebody,
            }

            return render(
                request,
                'subscribers/dashboard.html',
                context
            )

        else:
            return redirect(reverse('home'))
