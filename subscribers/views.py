from django.http import HttpResponse, HttpResponseNotFound, Http404
from django.shortcuts import render, render_to_response, redirect
from django.urls import reverse
from django.views.generic import TemplateView


from subscribers.forms import LoginForm, SubscriptionForm, PasswordCreationForm
from subscribers.models import Subscriber

class HomeView(TemplateView):
	template_name = 'home.html'

	def get(self, request, ref_code=None):
		form = SubscriptionForm()
		context = {
			'form': form,
		}
		ref_code = request.GET.get('ref_code', None)
		if ref_code:
			request.session['ref_code'] = ref_code

		return render(
			request,
			'subscribers/home.html',
			context
		)
	#Check if it is compulsory to set a default for ref_code as in Flask
	def post(self, request, ref_code=None):
		form = SubscriptionForm(request.POST)
		#if valid ref code means it's referred by someone
		if form.is_valid():
			email = form.cleaned_data['email']
			ip_from_user = request.META.get('REMOTE_ADDR', '0')

			if request.session.get('ref_code', False):
				email_from_referrer = Subscriber.objects.filter(unique_code=request.session['ref_code']).first()
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
			#better to force confirmation to update referral count from referrer
			#referrer = Subscriber.objects.filter(email=email_from_referrer).update(referral_count=F('referral_count') + 1)
			subscriber = Subscriber.objects.filter(email=email).first()
			#should I add here a context depending if the user is created or not
			#but w/o confirmation
			if created:
				return redirect(reverse('confirmation_prompt'))

			elif subscriber.confirmed_subscription == False:
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

class LoginView(TemplateView):
	template_name = 'login.html'

	def get(self, request):
		form = LoginForm()

		context = {
			'form': form,
		}

		return render(
			request,
			'subscribers/login.html',
			context
		)

	def post(self, request):
		pass

class ConfirmationView(TemplateView):
	template_name = 'confirmation.html'

	def get(self, request):
		context = {}

		return render(
			request,
			'subscribers/confirmation.html',
			context
		)

class CreatePassword(TemplateView):
	template_name = 'create_password.html'

	def get(self, request):
		form = PasswordCreationForm()
		context = {
			'form': form,
		}

		return render(
			request,
			'subscribers/create_password.html',
			context
		)

	def post(self, request):
		pass


class MailChimpListenerView(TemplateView):

	def get(self, request):
		context = {}

		return render_to_response("404.html", context, status=404)

	def post(self, request):
		pass
