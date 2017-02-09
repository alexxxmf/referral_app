from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import render, render_to_response
from django.views.generic import TemplateView

from subscribers.forms import SubscriptionForm
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
	#Check if it is compulsory tos et a default for ref_code as in Flask
	def post(self, request, ref_code=None):
		form = SubscriptionForm(request.POST)
		#if valid ref code means it's referred by someone
		if form.is_valid():
			email = form.cleaned_data['email']
			ip_from_user = request.META.get('REMOTE_ADDR', '0')

			if request.session['ref_code']:
				email_from_referrer = Subscriber.objects.filter(unique_code=ref_code).first()
				if email_from_referrer:
					referred = True
				else:
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

			if created:
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

class MailChimpListenerView(TemplateView):

	def get(self, request):
		return redirect(reverse('home'))

	def post(self, request):
		pass
