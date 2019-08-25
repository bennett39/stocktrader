from django.shortcuts import render
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin

from .exceptions import NotEnoughCashError, NotEnoughSharesError
from .forms import BuyForm, SellForm, QuoteForm
from .logic import (
    build_portfolio,
    process_transaction,
    apology,
    lookup_price,
    usd,
)
from .models import Profile, Stock, Transaction


class HomeView(LoginRequiredMixin, View):
    """ Display user's current portfolio balances """
    def get(self, request):
        profile = Profile.objects.get(user=request.user)
        portfolio = build_portfolio(profile.transactions.all())
        p_sum = sum((d['value'] for d in portfolio.values()))
        total = p_sum + profile.cash
        for d in portfolio.values():
            d['value'] = usd(d['value'])
        context = {
            'portfolio': portfolio,
            'cash': usd(profile.cash),
            'total': usd(total),
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


class QuoteView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'stocktrader/quote.html', {'form': QuoteForm()})

    def post(self, request):
        form = QuoteForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            try:
                quote = lookup_price(data['symbol'])
            except Exception as e:
                error = ('Problem looking up that symbol', e)
                return apology(request, error)
            return render(request, 'stocktrader/quoted.html', {'quote': quote})
        else:
            error = ('Invalid form input', )
            return apology(request, error)


class HistoryView(LoginRequiredMixin, View):
    def get(self, request):
        profile = Profile.objects.get(user=request.user)
        transactions = Transaction.objects.filter(user=profile)
        context = {
            'profile': profile,
            'transactions': [{
                'name': t.stock.name,
                'symbol': t.stock.symbol,
                'buy_sell': 'BUY' if t.quantity > 0 else 'SELL',
                'quantity': t.quantity,
                'price': usd(t.price),
                'total': usd(t.price * t.quantity),
                'time': t.time
            } for t in transactions],
        }
        return render(request, 'stocktrader/history.html', context)
