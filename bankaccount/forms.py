from django import forms
from .models import *


# форма для создания счета
class CreateBankAccountForm(forms.ModelForm):
    class Meta:
        model = BankAccounts
        fields = ['account_type', 'balance', 'currency']
        # название в поле field должен совпадать с тем что снизу
        account_type = forms.ChoiceField(label='Тип счета', choices=BankAccounts.BankAccounts_TYPES)
        balance = forms.DecimalField(label='Баланс')
        currency = forms.ChoiceField(label='Валюта', choices=BankAccounts.Currency_TYPES)


class MoneyTransferForm(forms.ModelForm):
    class Meta:
        model = MoneyTransfer
        fields = ['sender_id', 'source_account_number', 'destination_account_number', 'amount']

    sender_id = forms.ModelChoiceField(
        label='Счет отправителя',
        queryset=BankAccounts.objects.none(),
        to_field_name='id',
    )
    source_account_number = forms.CharField(label='Счет отправителя', required=False )
    destination_account_number = forms.CharField(label='Счет получателя')
    amount = forms.DecimalField(label='Cумма отправки')

    confirmation_code = forms.CharField(label='Код подтверждения', required=False)

    def __init__(self, *args, user=None, **kwargs):
        super(MoneyTransferForm, self).__init__(*args, **kwargs)
        self.fields['sender_id'].queryset = BankAccounts.objects.filter(user=user)


