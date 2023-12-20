from django.contrib.messages import get_messages
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from .models import BankAccounts, MoneyTransfer
from .forms import CreateBankAccountForm, MoneyTransferForm

User = get_user_model()


class BankAccountTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.login(username='testuser', password='testpassword')

    def test_createValidBankAccount(self):
        response = self.client.post(reverse('bankaccount'), {
            'account_type': 'checking_account',
            'balance': 1000,
            'currency': 'BYN',
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(BankAccounts.objects.count(), 1)
        # убеждаемся что созданный объект принадлежит пользователю по id
        self.assertEqual(BankAccounts.objects.first().user, self.user)

    def test_createInvalidBankAccount(self):
        form_data = {
            'account_type': 'checking_account',
            'balance': -1000,
            'currency': 'BYN',
        }
        response = self.client.post(reverse('bankaccount'), form_data)

        form = CreateBankAccountForm(data=form_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(BankAccounts.objects.count(), 0)
        # в общем тут я забыл сделать валидатор изначально для поле с суммой, поэтому проверка идет внутри метода
        self.assertTrue(form.is_valid())
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertIn('Нельзя ввести сумму больше 2000s или меньше 0.', messages)

    def test_createLimitBankAccount(self):
        BankAccounts.objects.create(user=self.user, account_type='checking_account', balance=1000, currency='USD')
        BankAccounts.objects.create(user=self.user, account_type='checking_account', balance=2000, currency='USD')

        form_data = {
            'account_type': 'checking_account',
            'balance': 2000,
            'currency': 'USD',
        }
        response = self.client.post(reverse('bankaccount'), form_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(BankAccounts.objects.filter(user=self.user, currency='USD').count(), 2)
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertIn('Вы достигли лимита создания счетов типа " Американский доллар".', messages)
        # сразу же тут проверка того что отобразаились 2 счета с USD
        self.assertContains(response, 'USD')
        self.assertContains(response, 'USD')


class MoneyTransferTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.login(username='testuser', password='testpassword')
        self.source_account = BankAccounts.objects.create(user=self.user, account_type='checking_account', balance=1500,
                                                          currency='EUR')
        self.destination_account = BankAccounts.objects.create(user=self.user, account_type='checking_account', balance=1500,
                                                          currency='USD')

    def test_validMoneyTransfer(self):
        form_data = {
            'sender_id': self.source_account.id,
            'source_account_number': self.source_account.account_number,
            'destination_account_number': self.destination_account.account_number,
            'amount': 500,
            'confirmation_code': '',
        }
        response = self.client.post(reverse('money_transfer'), form_data)
        # не 302, потому что результат происходит в том же url
        self.assertEqual(response.status_code, 200)
        self.assertEqual(MoneyTransfer.objects.count(), 1)
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertIn('Перевод был успешно совершен', messages)

    def test_invalidMoneyTransfer(self):
        form_data = {
            'sender_id': self.source_account.id,
            'source_account_number': self.source_account.account_number,
            'destination_account_number': self.source_account.account_number,
            'amount': 500,
            'confirmation_code': '',
        }
        response = self.client.post(reverse('money_transfer'), form_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(MoneyTransfer.objects.count(), 0)
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertIn('Вы не можете отправить на тот же счет средства!!!', messages)

    def test_MoneyTransferConfirmationCode(self):
        form_data = {
            'sender_id': self.source_account.id,
            'source_account_number': self.source_account.account_number,
            'destination_account_number': self.destination_account.account_number,
            'amount': 1010,
            'confirmation_code': '12345',
        }
        # для того, чтобы протестировать этот тест - нужно в confirmation_code поставить дефолтное значение
        response = self.client.post(reverse('money_transfer'), form_data)
        self.assertEqual(response.status_code, 200)
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertIn('Перевод был успешно совершен', messages)
        self.source_account.refresh_from_db()
        self.assertEqual(self.source_account.balance, 490)#
        money_transfer = MoneyTransfer.objects.first()
        self.assertEqual(money_transfer.source_account_number, self.source_account.account_number)
        self.assertEqual(money_transfer.destination_account_number, self.destination_account.account_number)
        self.assertEqual(money_transfer.amount, 1010)
        self.assertEqual(money_transfer.sender_id_id, self.source_account.id)
        self.assertEqual(money_transfer.recipient_id_id, self.destination_account.id)