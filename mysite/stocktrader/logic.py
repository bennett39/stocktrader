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
        portfolio[symbol]['value'] = usd(value)
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


def create_transaction(user, stock, quantity, price):
    """ Create a new Transaction and save it to db """
    from .models import Transaction
    order = Transaction(
        user=profile,
        stock=stock,
        quantity=quantity,
        price=price
    )
    order.save()


def get_stocks():
    """
    Loads stocks from JSON file on server
    """
    stocks = {}
    with open('stocks.json') as f:
        import json
        stocks = json.load(f)
    return stocks


def lookup_price(symbol):
    """
    Look up a quote for a stock symbol.
    https://iexcloud.io/docs/api/#quote
    """
    import os
    from dotenv import load_dotenv
    import requests
    load_dotenv()
    try:
        base = "https://cloud.iexapis.com/"
        version = "stable"
        endpoint = f"/stock/{symbol}/quote?token="
        public_token = os.getenv('PUBLIC_TOKEN')
        response = requests.get(
            ''.join((base, version, endpoint, public_token))
        )
        response.raise_for_status()
    except requests.RequestException as e:
        print(e)
        return None
    try:
        quote = response.json()
        return {
            'symbol': quote['symbol'],
            'name': quote['companyName'],
            'price': quote['latestPrice'],
        }
    except (KeyError, TypeError, ValueError) as e:
        print(e)
        return None


def update_user_cash(profile, amount):
    """ Add/subtract cash from a User's Profile """
    if profile.cash + amount > 0:
        profile.cash += amount
        profile.save()
    else:
        from .exceptions import NotEnoughCashError
        raise NotEnoughCashError


def usd(value):
    """ Format value as USD """
    return f"${value:,.2f}"