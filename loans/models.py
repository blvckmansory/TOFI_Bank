import uuid

from django.core.validators import *
from django.db import models
from users.models import Users
from mybank.FernetFile import *

from datetime import datetime, timedelta


class Loans(models.Model):
    Loans_TYPE = (
         ('Consumer_loan', 'Потребительский кредит'),
         ('Mortgage_loan', 'Ипотечный кредит'),
         ('Auto_loan', 'Автокредит'),
    )

    Currency_TYPES_Loans = (
        ('BYN', 'Белорусский рубль'),
        ('USD', 'Американский доллар'),
        ('EUR', 'Евро'),
    )

    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    loan_number = models.CharField(max_length=255, blank=False, null=False, unique=True,
                                      validators=[MinLengthValidator(16)])
    # сумму выдачи, которую пользователь выбрал
    issue_amount = models.DecimalField(max_digits=6, decimal_places=0, blank=False)

    # сумма возврата с процентами
    refund_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=False)
    # сколько уже оплатили
    paid = models.DecimalField(max_digits=10, decimal_places=2, blank=False)
    # остаток
    remainder = models.DecimalField(max_digits=10, decimal_places=2, blank=False)
    # платеж в месяц
    payment_amount_per_month = models.DecimalField(max_digits=8, decimal_places=2, blank=False)
    currency_loan = models.CharField(max_length=3, choices=Currency_TYPES_Loans)
    months = models.IntegerField(null=True)
    date_of_start = models.DateField(auto_now_add=True)
    date_of_end = models.DateField()
    loan_type = models.CharField(max_length=100, choices=Loans_TYPE, null=False)
    destination_account_number = models.CharField(max_length=255, null=True)
    # статус для того, чтобы потом ограничить возможность оплаты суммы кредита, когда он уже закрыт
    status = models.CharField(max_length=15, blank=False, null=False)

    def save(self, *args, **kwargs):
        if not self.loan_number:
            self.loan_number = uuid.uuid4().hex[:16].upper()

        # self.loan_number = fernet_encrypt(self.loan_number)

        super().save(*args, **kwargs)

    # def decrypted_loan_number(self):
    #     return fernet_decrypt(self.loan_number)


class Loan_History(models.Model):
    loan = models.ForeignKey(Loans, on_delete=models.CASCADE)
    loan_number = models.CharField(max_length=20, blank=False, null=False)
    summ_of_payment = models.DecimalField(max_digits=8, decimal_places=2, blank=False)
    remainder = models.DecimalField(max_digits=10, decimal_places=2, blank=False)
    currency = models.CharField(max_length=20)
    date_of_payment = models.DateField()
    status = status = models.CharField(max_length=15, blank=False, null=False)