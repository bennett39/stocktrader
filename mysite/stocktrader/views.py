from django.shortcuts import render
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin

from .exceptions import NotEnoughCashError, NotEnoughSharesError
from .forms import BuyForm, SellForm
from .logic import build_portfolio, process_transaction
from .models import Profile, Stock, Transaction


class HomeView(LoginRequiredMixin, View):
    """ Display user's current portfolio balances """
    def get(self, request):
        profile = Profile.objects.get(user=request.user)
        portfolio = build_portfolio(profile.transactions.all())
        context = {
            'profile': profile,
            'portfolio': portfolio,
        }
        return render(request, 'stocktrader/index.html', context)


class BuyView(LoginRequiredMixin, View):
    """
    Via GET: Show a BuyForm to purchase new stocks
    Via POST: Process BuyForm (see logic.py => process_transaction())
    """

    def get(self, request):
        context = { 'form': BuyForm() }
        return render(request, 'stocktrader/buy.html', context)

    def post(self, request):
        profile = Profile.objects.get(user=request.user)
        form = BuyForm(request.POST)
        if form.is_valid():
            return process_transaction(profile, form, request)
        else:
            print(form.errors)
            return self.get(request)


class SellView(LoginRequiredMixin, View):
    """
    Via GET: Display a SellForm for users to sell stocks
    Via POST: Process SellForm (see logic.py => process_transaction())
    """
    def get(self, request):
        profile = Profile.objects.get(user=request.user)
        portfolio = build_portfolio(profile.transactions.all())
        context = {
            'form': SellForm(portfolio=portfolio),
        }
        return render(request, 'stocktrader/sell.html', context)

    def post(self, request):
        profile = Profile.objects.get(user=request.user)
        portfolio = build_portfolio(profile.transactions.all())
        form = SellForm(request.POST, portfolio=portfolio)
        if form.is_valid():
            return process_transaction(profile, form, request)
        else:
            print(form.errors)
            return self.get(request)
