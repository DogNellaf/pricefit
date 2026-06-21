from decimal import Decimal

from django import forms

from .models import Request, TargetGroup


class RequestForm(forms.ModelForm):
    class Meta:
        model = Request
        fields = ['min_price', 'max_price']
        widgets = {
            'min_price': forms.NumberInput(
                attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}
            ),
            'max_price': forms.NumberInput(
                attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}
            ),
        }

    def clean(self):
        data = super().clean()
        min_price = data.get('min_price')
        max_price = data.get('max_price')

        if min_price is not None and min_price < Decimal('0'):
            self.add_error('min_price', 'Цена не может быть отрицательной.')
        if max_price is not None and max_price < Decimal('0'):
            self.add_error('max_price', 'Цена не может быть отрицательной.')
        if min_price is not None and max_price is not None and min_price > max_price:
            self.add_error(
                'max_price', 'Максимальная цена должна быть не меньше минимальной.'
            )
        return data


class TargetGroupForm(forms.ModelForm):
    class Meta:
        model = TargetGroup
        fields = ['title', 'description', 'min_budget', 'max_budget']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'min_budget': forms.NumberInput(
                attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}
            ),
            'max_budget': forms.NumberInput(
                attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}
            ),
        }

    def clean(self):
        data = super().clean()
        min_budget = data.get('min_budget')
        max_budget = data.get('max_budget')

        if min_budget is not None and max_budget is not None and min_budget > max_budget:
            self.add_error(
                'max_budget', 'Максимальный бюджет должен быть не меньше минимального.'
            )
        return data
