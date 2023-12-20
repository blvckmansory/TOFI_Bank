from django.http import HttpResponse, HttpResponseNotFound, JsonResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.utils import timezone
import random
import requests
from decimal import Decimal

from loans.models import Loan_History
from .models import *

# Create your views here.
from bankaccount.forms import *

menu = [
    # {'title': 'Личный кабинет', 'url_name': 'account_settings'},
    {'title': 'Просмотр счетов', 'url_name': 'bankaccount'},
    {'title': 'Денежные переводы', 'url_name': 'money_transfer'},
    {'title': 'Оформление кредита', 'url_name': 'apply_for_loan'},
    {'title': 'Платежи', 'url_name': 'payments'},
    {'title': 'История транзакций', 'url_name': 'money_transfer_history'},
]


# Банковский счет
def bankaccount_index(request):

    if request.method == 'POST':
        form = CreateBankAccountForm(request.POST)
        if form.is_valid():
            # для проверки баланса (тоже ставим ограничение)
            balance = form.cleaned_data['balance']

            # Сделаем лимит на количество создания счетов, чтобы нельзя было миллионов наделать
            account_type_name = form.cleaned_data['account_type']
            currency_type = form.cleaned_data['currency']

            # existing_accounts_count = BankAccounts.objects.filter(user=request.user, account_type=account_type_name).count()
            existing_accounts_count = BankAccounts.objects.filter(user=request.user, currency=currency_type).count()
            limit = 2
            # Нужно продумать про кредитный счет (скорее всего нужно убрать и сделать отдельно)

            if balance > 2000 or balance < 0:
                messages.error(request, 'Нельзя ввести сумму больше 2000s или меньше 0.')
            elif existing_accounts_count >= limit:
                # display_account_type = BankAccounts.ACCOUNT_TYPES_DICT.get(account_type_name, account_type_name)
                display_account_type = BankAccounts.CURRENCY_TYPES_DICT.get(currency_type, currency_type)
                messages.error(request, f'Вы достигли лимита создания счетов типа " { display_account_type }".')
            else:
                # Чтобы не забыть: сначала мы сохраняем данные карты а потом внешний ключ добавляем к записи
                bank_account = form.save(commit=False)
                bank_account.user = request.user
                bank_account.save()

                send_email_user_bankaccount(bank_account.account_number, bank_account.currency, request.user.email)

                messages.success(request, 'Счет успешно создан!')
                return redirect('bankaccount')

    else:
        form = CreateBankAccountForm()

    context = {
        'title': 'Банковские счета',
        'menu': menu,
        'form': form,
    }
    return render(request, 'bankaccount/Checking_BankAccount.html', context)


# Денежные переводы
def money_transfer_index(request):
    if request.method == 'POST':
        form = MoneyTransferForm(request.POST, user=request.user)

        if form.is_valid():
            print("Cleaned data:", form.cleaned_data)

            # получение оъекта
            source_account_number = form.cleaned_data['sender_id'].account_number
            destination_account_number = form.cleaned_data['destination_account_number']
            amount = form.cleaned_data['amount']

            # получение счетов отправителя и получателя , конвертаци я оъекта в строку
            source_account = BankAccounts.objects.get(account_number=str(source_account_number))
            fromCurrency = source_account.currency

            try:
                destination_account = BankAccounts.objects.get(account_number=destination_account_number)
            except BankAccounts.DoesNotExist:
                messages.error(request, 'Карточного счета с указанным номером не существует')
                return redirect('money_transfer')
            toCurrency = destination_account.currency

            converted_amount = convert_currency(amount, toCurrency, fromCurrency)

            if amount > 1000:

                if 'confirmation_code' in request.session:
                    confirmation_code = request.session['confirmation_code']
                else:
                    confirmation_code = ''.join(random.choices('0123456789', k=6))
                    # confirmation_code = '12345'
                    send_email_user(confirmation_code, request.user.email)

                request.session['confirmation_code'] = confirmation_code

                if 'request_new_code' in request.POST:
                    # Проверка времени последней отправки кода
                    user_last_confirmation_code_sent = request.user.last_confirmation_code_sent
                    if user_last_confirmation_code_sent and (
                            timezone.now() - user_last_confirmation_code_sent).seconds < 60:
                        messages.error(request, 'Вы можете запросить новый код только раз в минуту')
                        # return redirect('money_transfer')
                    else:
                        confirmation_code = generate_acception_code()
                        send_email_user(confirmation_code, request.user.email)

                        request.user.last_confirmation_code_sent = timezone.now()
                        request.user.save()

                        request.session['confirmation_code'] = confirmation_code

                        messages.success(request, 'Новый код подтверждения был отправлен на вашу почту')
                        # return redirect('money_transfer')

                if 'confirmation_code' in request.POST:
                    messages.info(request, 'Для продолжения операции вы должны вести код подтверждения, который присылается на вашу почту!')
                    user_confirmation_code = request.POST['confirmation_code']

                    if user_confirmation_code == confirmation_code:
                        transfer_operation(destination_account, source_account, amount, converted_amount, request)
                    else:
                        if user_confirmation_code.strip():
                            messages.error(request, 'Неверный код подтверждения')
                else:
                    messages.error(request, 'Введите код подтверждения')
            # чтобы просто видеть где меньше 1000
            else:
                transfer_operation(destination_account, source_account, amount, converted_amount, request)
        else:
            print("Form errors:", form.errors)
            messages.error(request, 'Вы ввели некорректные данные!')

    else:
        form = MoneyTransferForm(user=request.user)

    context = {
        'title': 'Денежные переводы',
        'menu': menu,
        'form': form,
    }
    return render(request, 'bankaccount/Money_Transfer.html', context)


def transfer_operation(destination_account, source_account, amount, converted_amount, request):
    if destination_account == source_account:
        messages.error(request, 'Вы не можете отправить на тот же счет средства!!!')
    elif source_account.balance >= amount:
        if amount >= 3:
            perform_transfer(source_account, destination_account, amount, converted_amount)
            messages.success(request, 'Перевод был успешно совершен')

            if 'confirmation_code' in request.session:
                del request.session['confirmation_code']

            return redirect('money_transfer')
        else:
            messages.error(request, 'Ошибка ввода сумму перевода!')
    else:
        messages.error(request, 'Недостаточно средств для перевода')


# def money_transfer_info(request):
#
#     if request.method == 'POST':
#         form = MoneyTransferForm(request.POST, user=request.user)
#
#         if form.is_valid():
#             destination_account_number = form.cleaned_data['destination_account_number']
#             try:
#                 destination_account = BankAccounts.objects.get(account_number=destination_account_number)
#                 username = destination_account.user_id.user.username
#                 context = {
#                     'title': 'Денежные переводы',
#                     'menu': menu,
#                     'form': form,
#                     'username': username,
#                 }
#                 return render(request, 'bankaccount/Money_Transfer.html', context)
#             except BankAccounts.DoesNotExist:
#                 messages.error(request, 'Карточного счета с указанным номером не существует')
#             return redirect('money_transfer')
#
#         context = {
#             'title': 'Денежные переводы',
#             'menu': menu,
#             'form': form,
#         }
#         return render(request, 'bankaccount/Money_Transfer.html', context)


def money_transfer_history(request):
    transfers = MoneyTransfer.objects.filter(sender_id__user=request.user)
    payments = Loan_History.objects.filter(loan_id__user=request.user)
    context = {
        'title': 'История транзакций',
        'menu': menu,
        'transfers': transfers,
        'payments': payments,
    }
    return render(request, 'bankaccount/money_transfer_history.html', context)


def send_email_user(confirmation_code, email):
    send_mail(
        'Код подтверждения перевода',
        f'Ваш код подтверждения: {confirmation_code}',
        'settings.EMAIL_HOST_USER',
        [email],
        fail_silently=False,
    )


def send_email_user_bankaccount(bankaccount, currency, email):
    subject = 'MyBank'
    message = (
        f'Уважаемый клиент, поздравляем вас с открытием нового счета в MyBank!\n'
        f'Ваш номер счета: {bankaccount} {currency}\n'
        f'Никому не сообщайте свой номер счета для обеспечения безопасности.\n\n'
        f'Вы можете войти в личный кабинет MyBank и управлять своим счетом.\n'
    )

    send_mail(
        subject,
        message,
        'settings.EMAIL_HOST_USER',
        [email],
        fail_silently=False,
    )


def perform_transfer(source_account, destination_account, amount, converted_amount):
    source_account.balance -= amount
    destination_account.balance += converted_amount
    source_account.save()
    destination_account.save()

    MoneyTransfer.objects.create(
        source_account_number=source_account.account_number,
        destination_account_number=destination_account.account_number,
        sender_id=source_account, recipient_id=destination_account,
        amount=amount, converted_amount=converted_amount
    )


def generate_acception_code():
    return ''.join(random.choices('0123456789', k=6))


def convert_currency(amount, toCurrency, fromCurrency):
    # API
    url = f"https://api.exchangerate-api.com/v4/latest/{fromCurrency}"
    response = requests.get(url)
    data = response.json()
    exchange_rate = Decimal(data['rates'][toCurrency])
    converted_amount = amount*exchange_rate
    return converted_amount


def categories(request, categoryID):
    if request.GET:
        print(request.GET)
    return HttpResponse(f"<h1>Hi world</h1><p>{categoryID}</p>")


def pageNotFound(request, exception):
    return HttpResponseNotFound('<h1>Страница не найдена</h1>')


