from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Profile, Stock, Transaction
from .logic import *
from .forms import BuyForm, SellForm
from .exceptions import *


class HomeView(LoginRequiredMixin, View):
    """ Display user's current portfolio balances """
    def get(self, request):
        profile = Profile.objects.get(user=request.user)
        portfolio = build_portfolio(profile.transactions.all())
        context = {
            'profile': profile,
            'portfolio': portfolio,
            'stocks': get_stocks(),
        }
        return render(request, 'stocktrader/index.html', context)


class BuyView(LoginRequiredMixin, View):
    """
    Via GET: Show a BuyForm to purchase new stocks
    Via POST: Process BuyForm, creating a new Transaction object in db
    and updating user.profile.cash
    """

    def get(self, request):
        context = {
            'stocks': get_stocks(),
            'form': BuyForm(),
        }
        return render(request, 'stocktrader/buy.html', context)

    def post(self, request):
        profile = Profile.objects.get(user=request.user)
        form = BuyForm(request.POST)
        if form.is_valid():
            return process_transaction(profile, form, True, request)
        else:
            print(form.errors)
            return self.get(request)


class SellView(LoginRequiredMixin, View):
    """
    Via GET: Display a SellForm for users to sell stocks.
    Via POST: Process SellForm to create a Transaction in db and update
    user.profile.cash
    """
    def get(self, request):
        profile = Profile.objects.get(user=request.user)
        portfolio = build_portfolio(profile.transactions.all())
        context = {
            'stocks': get_stocks(),
            'form': SellForm(portfolio=portfolio),
        }
        return render(request, 'stocktrader/sell.html', context)

    def post(self, request):
        profile = Profile.objects.get(user=request.user)
        portfolio = build_portfolio(profile.transactions.all())
        form = SellForm(request.POST, portfolio=portfolio)
        if form.is_valid():
            return process_transaction(profile, form, False, request)
        else:
            print(form.errors)
            return self.get(request)



def apology(request, error):
    """
    Print error in logs and render the error to user via apology.html
    template.
    """
    print(error)
    return render(request, 'stocktrader/apology.html', {'error': error})


def process_transaction(profile, form, is_buy, request):
    data, error = form.cleaned_data, None
    try:
        quote = lookup_price(data['symbol'])
        total = data['quantity'] * quote['price']
    except Exception as e:
        error = ('No quote available - check API', e)
        return apology(request, error)
    try:
        stock, created = Stock.objects.get_or_create(
            name=quote['name'],
            symbol=quote['symbol']
        )
        transaction = Transaction(
            user=profile,
            stock=stock,
            quantity=data['quantity'] if is_buy else -data['quantity'],
            price=quote['price']
        )
        update_user_cash(profile, -total if is_buy else total)
        # ^^ Make sure user has the cash before saving transaction.
        transaction.save() # Make sure transaction saves successfully
        profile.save() # ...before saving the new cash balance
    except NotEnoughCashError:
        error = (
            'Not enough cash to buy that stock',
            f'Order total was {usd(total)} and you have {usd(profile.cash)}'
        )
        return apology(request, error)
    except Exception as e:
        print(e)
        error = ('Problem saving order', e)
        return apology(request, error)
    return redirect('home')

