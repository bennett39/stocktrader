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


def get_stocks():
    """
    Loads stocks from JSON file on server
    """
    with open('stocks.json') as f:
        import json
        return json.load(f)


def lookup_price(symbol):
    """
    Look up a quote for a stock symbol.
    https://iexcloud.io/docs/api/#quote
    """
    import os
    import requests
    from dotenv import load_dotenv
    load_dotenv()
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


def update_user_cash(profile, amount):
    """ Add/subtract cash from a User's Profile """
    if profile.cash + amount > 0:
        profile.cash += amount
    else:
        from .exceptions import NotEnoughCashError
        raise NotEnoughCashError


def usd(value):
    """ Format value as USD """
    return f"${value:,.2f}"
