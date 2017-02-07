from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import render
from django.views.generic import TemplateView

from subscribers.forms import SubscriptionForm
from subscribers.models import Subscriber

class HomeView(TemplateView):
	template_name = 'home.html'

	def get(self, request):
		form = SubscriptionForm()
		context = {
			'form': form,
		}
		return render(
			request,
			'subscribers/home.html',
			context
		)

	def post(self, request):
		form = SubscriptionForm(request.POST)
		#if valid ref code means it's referred by someone
		if form.is_valid():
			email = form.cleaned_data['email']
			ip_from_user = request.META.get('REMOTE_ADDR', '0')
			subscriber, created = Person.objects.get_or_create(
			    email=email,
			    defaults={'ip':ip_from_user},
			)
			if created:
				#Subscriber already in db
				return redirect(reverse('login'))
			else:
				return redirect(reverse('confirmation_prompt'))

		context = {
			'form': form,
		}
		return render(
			request,
			'subscribers/home.html',
			context
		)
