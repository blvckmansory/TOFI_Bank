from django.contrib import messages
from datetime import datetime, timedelta

from django.core.mail import send_mail
from django.shortcuts import render, redirect
from decimal import Decimal

from django.utils import timezone

from bankaccount.forms import MoneyTransferForm
from bankaccount.models import BankAccounts
from bankaccount.views import convert_currency
from loans.forms import MakeALoanForm
from loans.models import Loans, Loan_History
from mybank.FernetFile import *

menu = [
    # {'title': 'Личный кабинет', 'url_name': 'account_settings'},
    {'title': 'Просмотр счетов', 'url_name': 'bankaccount'},
    {'title': 'Денежные переводы', 'url_name': 'money_transfer'},
    {'title': 'Оформление кредита', 'url_name': 'apply_for_loan'},
    {'title': 'Платежи', 'url_name': 'payments'},
    {'title': 'История транзакций', 'url_name': 'money_transfer_history'},
]


def apply_loan_index(request):
    if request.method == 'POST':
        form = MakeALoanForm(request.POST, user=request.user)

        if form.is_valid():
            print("Cleaned data:", form.cleaned_data)

            date_of_birth = request.user.documents.date_of_birth
            age = calculate_age(date_of_birth)

            if age < 18:
                messages.error(request, f'Извините, но мы отказываемся вам выдавать кредит в вашем возрасте: {age}')
                return redirect('apply_for_loan')

            loan_type = form.cleaned_data['loan_type']
            months = form.cleaned_data['months']
            issue_amount = form.cleaned_data['issue_amount']
            currency_loan = form.cleaned_data['currency_loan']
            destination_account_number = form.cleaned_data['destination_account_number']
            #destination_account_number_get = fernet_encrypt(str(destination_account_number))
            #messages.error(request, destination_account_number_get)

            existing_loans_count = Loans.objects.filter(user=request.user, status='Оплачивается').count()
            limit = 2

            try:
                destination_account = BankAccounts.objects.get(account_number=destination_account_number,
                                                               user=request.user)
            except BankAccounts.DoesNotExist:
                destination_account = None
                messages.error(request, 'Счет не существует или не принадлежит текущему пользователю!')

            if months < 1 or months > 360:
                messages.error(request, 'Введите значения от 1 месяца до 360 (30 лет)')
            elif issue_amount < 100 or issue_amount > 100000:
                messages.error(request, 'Минимальная сумма кредита: 100 у.е. \nМаксимальная сумма кредита: 100000 у.е.')
            elif currency_loan != destination_account.currency:
                messages.error(request, 'Данный счет не в той же валюте что вы выбрали.')
            elif existing_loans_count == limit:
                messages.error(request, 'Вы достигли лимит оформления кредита, закройте, пожалуйста ваши задолженности.')
            else:
                loan = form.save(commit=False)
                loan.user = request.user
                loan.status = 'Оплачивается'
                loan.paid = 0

                loan.refund_amount = calculated_refund_amount(loan_type, issue_amount, months)
                loan.remainder = loan.refund_amount - loan.paid
                loan.payment_amount_per_month = loan.refund_amount / months
                loan.date_of_start = datetime.now()
                loan.date_of_end = datetime.now() + timedelta(days=30*months)

                destination_account.balance += issue_amount
                destination_account.save()

                loan.save()

                send_email_user_loan(loan.loan_number, loan.currency_loan, loan.status, request.user.email)

                messages.success(request, 'Кредит успешно оформлен!')
                return redirect('apply_for_loan')
        else:
            print("Form errors:", form.errors)
            messages.error(request, 'Вы ввели некорректные данные!')
    else:
        user = request.user
        loans = user.loans_set.all().order_by('-status')
        form = MakeALoanForm(user=request.user)

    context = {
        'title': 'Оформление кредита',
        'menu': menu,
        'loans': loans,
        'form': form

    }
    return render(request, 'loans/Apply_for_a_loan.html', context)


def send_email_user_loan(loan_number, currency, status, email):
    subject = 'MyBank'
    message = (
        f'Информация по кредиту! \n\n'
        f'Уважаемый клиент, мы одобрили вам ваш запрос на кредит!\n'
        f'Ваш номер кредитного счета: {loan_number} {currency}\n'
        f'Статус: {status}\n'
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


def calculate_age(date_of_birth):
    today = timezone.now().date()
    age = today.year - date_of_birth.year - ((today.month, today.day) < (date_of_birth.month, date_of_birth.day))
    return age


def payments_index(request):
    if request.method == 'POST':
        form = MoneyTransferForm(request.POST, user=request.user)

        if form.is_valid():
            print("Cleaned data:", form.cleaned_data)

            source_account_number = form.cleaned_data['sender_id'].account_number
            destination_account_number = form.cleaned_data['destination_account_number']
            amount = form.cleaned_data['amount']

            # Получение счетов отправителя и получателя
            source_account = BankAccounts.objects.get(account_number=str(source_account_number))
            fromCurrency = source_account.currency

            destination_account = Loans.objects.get(loan_number=destination_account_number)
            toCurrency = destination_account.currency_loan

            converted_amount = convert_currency(amount, toCurrency, fromCurrency)

            if source_account.balance >= amount:
                if 0 < amount <= destination_account.remainder and destination_account.status == 'Оплачивается':

                    source_account.balance -= amount
                    destination_account.paid += converted_amount
                    destination_account.remainder = destination_account.refund_amount - destination_account.paid
                    if destination_account.paid == destination_account.refund_amount:
                        destination_account.status = 'Закрыт'

                    source_account.save()
                    destination_account.save()

                    # Логирование
                    Loan_History.objects.create(
                        loan=destination_account,
                        loan_number=destination_account.loan_number,
                        summ_of_payment=converted_amount,
                        remainder=destination_account.remainder,
                        date_of_payment=datetime.now(),
                        currency=fromCurrency,
                        status=destination_account.status,
                    )

                    messages.success(request, 'Оплата была успешна завершена')
                    return redirect('payments')
                else:
                    messages.error(request, 'Ошибка ввода сумму перевода или неверный счет кредита!')
            else:
                messages.error(request, 'Недостаточно средств для перевода')
        else:
            print("Form errors:", form.errors)
            messages.error(request, 'Вы ввели некорректные данные!')

    else:
        form = MoneyTransferForm(user=request.user)

    context = {
        'title': 'Платежи',
        'menu': menu,
        'form': form,
    }

    return render(request, 'loans/Payments.html', context)


def calculated_refund_amount(loan_type, issue_amount, months):
    if loan_type == 'Consumer_loan':
        return calculated_result(15.25, months, issue_amount)

    if loan_type == 'Mortgage_loan':
        return calculated_result(12.5, months, issue_amount)

    if loan_type == 'Auto_loan':
        return calculated_result(9.5, months, issue_amount)


def calculated_result(procent, months, issue_amount):
    # Чтобы не забыть как считаются проценты годовых
    # Сначала нужно поделить общий процент на 100 и 12, чтобы получить проценты за ежемесячный платеж. То есть какой процент от суммы платежа в месяц
    # Потом уже вычисляем полную сумму добавки к запрашиваемой сумме (То есть это столько пользователь будет должен за определенный период)
    annual_interest_rate = procent / 100
    monthly_interest_rate = (annual_interest_rate / 12)
    total_interest = Decimal(monthly_interest_rate * months) * issue_amount
    total_payment = issue_amount + total_interest
    return total_payment