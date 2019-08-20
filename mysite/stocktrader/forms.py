from django import forms

class BuyForm(forms.Form):
    symbol = forms.CharField(label='Ticker Symbol', max_length=10)
    quantity = forms.DecimalField(
        label='Shares',
        max_digits=10,
        decimal_places=2,
    )
