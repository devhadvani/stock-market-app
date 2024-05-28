from django import forms

class StockSearchForm(forms.Form):
    symbol = forms.CharField(max_length=10, label='Stock Symbol')
