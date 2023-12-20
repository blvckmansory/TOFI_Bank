from django.contrib.messages import get_messages
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from pip._internal.utils import datetime
from datetime import datetime, timedelta
from .models import Loans, Loan_History
from .forms import MakeALoanForm
from bankaccount.models import BankAccounts

User = get_user_model()


class TestMakingLoans(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.login(username='testuser', password='testpassword')
        self.destination_account = BankAccounts.objects.create(user=self.user, account_type='checking_account', balance=1000,
                                                          currency='EUR')

    # def test_validLoanData(self):
    #     form_date = {
    #         'loan_type': 'Consumer_loan',
    #         'months': 12,
    #         'issue_amount': 10000,
    #         'currency_loan': 'EUR',
    #         'destination_account_number': self.destination_account,
    #     }
    #     response = self.client.post(reverse('apply_for_loan'), form_date)
    #     self.assertEqual(response.status_code, 302)
    #     self.assertEqual(Loans.objects.count(), 1)
    #     self.assertEqual(Loans.objects.first().user, self.user)

    def test_display_created_loans(self):
        loan = Loans.objects.create(
            user=self.user,
            loan_type='Consumer_loan',
            months=12,
            refund_amount=1300,
            paid=0,
            remainder=1200,
            issue_amount=1000,
            payment_amount_per_month=100,
            currency_loan='USD',
            destination_account_number='valid_account_number',
            date_of_start=datetime.now(),
            date_of_end=datetime.now() + timedelta(days=30 * 12),
            status='Оплачивается',
        )

        response = self.client.get(reverse('apply_for_loan'))
        self.assertContains(response, loan.get_loan_type_display())
        self.assertContains(response, loan.remainder)
        self.assertContains(response, loan.refund_amount)
        self.assertContains(response, loan.issue_amount)


class PaymentsTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.login(username='testuser', password='testpassword')
        self.sender_account = BankAccounts.objects.create(user=self.user, account_type='checking_account', balance=1000, currency='USD')

        self.loan = Loans.objects.create(user=self.user, loan_type='Consumer_loan', issue_amount=500, refund_amount=600,
                                         paid=100, remainder=500, payment_amount_per_month=100, currency_loan='USD',
                                         months=6, date_of_start=datetime.now(), date_of_end=datetime.now() + timedelta(days=30 * 12), status='Оплачивается')

    def test_valid_payment(self):
        response = self.client.post(reverse('payments'), {
            'sender_id': self.sender_account.id,
            'destination_account_number': self.loan.loan_number,
            'amount': 100,
            'status': 'Оплачивается'
        })
        self.assertEqual(response.status_code, 302)
        self.sender_account.refresh_from_db()
        self.assertEqual(self.sender_account.balance, 900)
        self.loan.refresh_from_db()
        self.assertEqual(self.loan.paid, 200)
        loan_history = Loan_History.objects.first()
        self.assertIsNotNone(loan_history)
        self.assertEqual(loan_history.loan, self.loan)
        self.assertEqual(loan_history.summ_of_payment, 100)
        self.assertEqual(loan_history.currency, 'USD')
        self.assertEqual(loan_history.status, self.loan.status)

    def test_invalid_payment(self):
        response = self.client.post(reverse('payments'), {
            'sender_id': self.sender_account.id,
            'destination_account_number': 'NSD8DSC4',
            'amount': 100,
            'status': 'Оплачивается'
        })
        self.assertEqual(response.status_code, 200)
        self.sender_account.refresh_from_db()
        self.assertEqual(self.sender_account.balance, 1000)
        self.loan.refresh_from_db()
        self.assertEqual(self.loan.paid, 100)
        loan_history = Loan_History.objects.first()
        self.assertIsNone(loan_history)

