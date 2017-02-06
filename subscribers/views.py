from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import render
from django.views.generic import TemplateView

from subscribers.forms import SubscriptionForm

class HomeView(TemplateView):
	template_name = 'home.html'

	def get(self, request):
		form = SubscriptionForm()
		context = {'form': form, }
		return render(request, 'subscribers/home.html', context)

	def post(self, request):
		return HttpResponse('a')
