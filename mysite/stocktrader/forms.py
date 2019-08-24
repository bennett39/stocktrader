from django import forms

class BuyForm(forms.Form):
    """ Puchases a stock for given user. """
    symbol = forms.CharField(
        label='Ticker Symbol',
        max_length=10
    )
    quantity = forms.FloatField(
        label='Shares',
        min_value=0.01
    )


class SellForm(forms.Form):
    """ Sells a stock that a given user already owns """
    symbol = forms.ChoiceField(
        label='Ticker Symbol',
        choices=[]
    )
    quantity = forms.FloatField(
        label='Shares',
        min_value=0.01
    )

    def __init__(self, *args, **kwargs):
        portfolio = kwargs.pop('portfolio', None)
        super().__init__(*args, **kwargs)
        if portfolio is not None:
            self.fields['symbol'].choices = [
                (s, d['name']) for s,d in portfolio.items()
            ]


class QuoteForm(forms.Form):
    symbol = forms.CharField(
        label='Ticker Symbol',
        max_length=10
    )
