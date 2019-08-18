from django.shortcuts import render
from django.http import HttpResponse
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Profile, Stock, Transaction

# Create your views here.
class HomeView(LoginRequiredMixin, View):
    def get(self, request):
        profile = Profile.objects.get(user=request.user)
        transactions = profile.transactions.all()

        return HttpResponse(f"""Hello {profile.user.username}, you have
        ${profile.cash}. Your transactions are
        {[t.__str__() for t in transactions]}.""")
