from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import render
from django.views.generic import TemplateView

class HomeView(TemplateView):
	template_name = 'home.html'

	def get(self, request):
		return render(request, 'subscribers/home.html')

	def post(self, request):
		return HttpResponse('a')