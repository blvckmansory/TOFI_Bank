from django import forms

from bankaccount.models import BankAccounts
from .models import *


class MakeALoanForm(forms.ModelForm):
    class Meta:
        model = Loans
        fields = ['loan_type', 'months', 'issue_amount', 'currency_loan', 'destination_account_number']

        loan_type = forms.ChoiceField(label='Тип кредита', choices=Loans.Loans_TYPE)
        months = forms.IntegerField(label='Месяцы')
        issue_amount = forms.DecimalField(label="Сумма кредита")
        currency_loan = forms.ChoiceField(label='Валюта кредита', choices=Loans.Currency_TYPES_Loans)

        destination_account_number = forms.ModelChoiceField(
            label='Счет получателя',
            queryset=BankAccounts.objects.none(),
            to_field_name='account_number',
        )

    def __init__(self, *args, user=None, **kwargs):
        super(MakeALoanForm, self).__init__(*args, **kwargs)
        self.fields['destination_account_number'].queryset = BankAccounts.objects.filter(user=user)
