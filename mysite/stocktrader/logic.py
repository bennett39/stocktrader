from dotenv import load_dotenv
load_dotenv()
import json
import os
import requests

from django.shortcuts import render, redirect

from .models import Stock, Transaction
from .exceptions import NotEnoughCashError, NotEnoughSharesError


def apology(request, error):
    """
    Print error in logs and render the error to user via apology.html
    template.
    """
    print(error)
    return render(request, 'stocktrader/apology.html', {'error': error})


def build_portfolio(transactions):
    """ Build portfolio of current stock values """
    stocks = count_shares_owned(transactions)
    portfolio = {}
    for stock, quantity in stocks.items():
        quote = lookup_price(stock)
        symbol = quote['symbol']
        value = quantity * quote['price']
        portfolio.setdefault(
            symbol,
            {'name': '', 'quantity': 0, 'value': 0}
        )
        portfolio[symbol]['name'] = quote['name']
        portfolio[symbol]['quantity'] = quantity
        portfolio[symbol]['value'] = value
    return portfolio


def count_shares_owned(transactions):
    """
    Sum the totals of buy/sell orders to get a current list of stocks
    owned.
    """
    stocks = {}
    for t in transactions:
        symbol = t.stock.symbol
        stocks.setdefault(symbol, 0)
        stocks[symbol] += t.quantity
        if stocks[symbol] == 0:
            del stocks[symbol]
    return stocks


def lookup_price(symbol):
    """
    Look up a quote for a stock symbol.
    https://iexcloud.io/docs/api/#quote
    """
    base = "https://cloud.iexapis.com"
    version = "/stable"
    endpoint = f"/stock/{symbol}/quote"
    token = f"?token={os.getenv('PUBLIC_TOKEN')}"
    response = requests.get(
        ''.join((base, version, endpoint, token))
    )
    response.raise_for_status()
    quote = response.json()
    return {
        'symbol': quote['symbol'],
        'name': quote['companyName'],
        'price': quote['latestPrice'],
    }


def process_transaction(profile, form, request):
    """
    Process form data to create a new Transaction and update
    Profile.cash in the db

    Args:
    - profile => Profile object of current user (see models.py)
    - form => form submitted via POST, either BuyForm or SellForm (forms.py)
    - request => request from view (views.py)
    """

    data, error = form.cleaned_data, None
    is_buy = not hasattr(form.fields['symbol'], 'choices')
    # Duck typing: SellForm has a choices attribute, BuyForm does not

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
        portfolio = build_portfolio(profile.transactions.all())
        if not is_buy and data['quantity'] > portfolio[stock.symbol]['quantity']:
            raise NotEnoughSharesError
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
    except NotEnoughSharesError:
        error = (
            'Trying to sell more shares than you own',
            f'Sell order was for {data["quantity"]} shares ' +
            f'and you only own {portfolio[stock.symbol]["quantity"]}'
        )
        return apology(request, error)
    except NotEnoughCashError:
        error = (
            'Not enough cash to buy that stock',
            f'Order total was {usd(total)} and you have {usd(profile.cash)}'
        )
        return apology(request, error)
    except Exception as e:
        error = ('Problem saving order', e)
        return apology(request, error)

    return redirect('home')



def update_user_cash(profile, amount):
    """ Add/subtract cash from a User's Profile """
    if profile.cash + amount > 0:
        profile.cash += amount
    else:
        raise NotEnoughCashError


def usd(value):
    """ Format value as USD """
    return f"${value:,.2f}"
