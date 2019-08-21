from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Profile, Stock, Transaction
from .logic import *
from .forms import BuyForm
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
        form = BuyForm(request.POST)
        if form.is_valid():
            profile = Profile.objects.get(user=request.user)
            data, error = form.cleaned_data, None
            try:
                quote = lookup_price(data['symbol'])
                total = float(data['quantity']) * quote['price']
                stock, created = Stock.objects.get_or_create(
                    name=quote['name'],
                    symbol=quote['symbol']
                )
            except Exception as e:
                error = ('No quote available - check API', e)
                return apology(request, error)
            try:
                create_transaction(
                    profile,
                    stock,
                    data['quantity'],
                    quote['price']
                )
            except Exception as e:
                error = ('Problem saving order', e)
                return apology(request, error)
            try:
                update_user_cash(profile, -total)
            except NotEnoughCashError:
                error = (
                    'Not enough cash to buy that stock',
                    f'Order total was {usd(total)} and you have {usd(profile.cash)}'
                )
            except Exception as e:
                error = ('Problem updating cash', e)
                return apology(request, error)
            return redirect('home')
        else:
            error = ('Invalid form input',)
            return apology(request, error)


def apology(request, error):
    print(error)
    return render(request, 'stocktrader/apology.html', {'error': error})
