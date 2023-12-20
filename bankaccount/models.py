import uuid

from django.core.validators import *
from django.db import models

from mybank import settings
from users.models import Users
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
from mybank import FernetFile


# key = settings.SECRET_KEY
# fernet = Fernet(key)


# Банковский счет
class BankAccounts(models.Model):
    BankAccounts_TYPES = (
        ('checking_account', 'Текущий счет'),
        #('loan_account', 'Кредитный счет'),
    )

    Currency_TYPES = (
        ('BYN', 'Белорусский рубль'),
        ('USD', 'Американский доллар'),
        ('RUB', 'Российский рубль'),
        ('EUR', 'Евро'),
        ('CNY', 'Китайский юань'),
    )

    # Чтобы вывести при ошибке второе значение списка, а не checking_account
    ACCOUNT_TYPES_DICT = dict(BankAccounts_TYPES)
    CURRENCY_TYPES_DICT = dict(Currency_TYPES)

    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    account_type = models.CharField(max_length=30, choices=BankAccounts_TYPES)
    account_number = models.CharField(max_length=255, blank=False, null=False, unique=True,
                                      validators=[MinLengthValidator(16)])
    balance = models.DecimalField(max_digits=10, decimal_places=2, blank=False)
    currency = models.CharField(max_length=3, choices=Currency_TYPES)
    expiration_date = models.DateField()

    def save(self, *args, **kwargs):
        # нужно также сгененрировать (уникальный) номер счета, а то из-за уникальности не добить счетов
        if not self.account_number:
            self.account_number = uuid.uuid4().hex[:16].upper()

        # encrypted_account_number = fernet.encrypt(self.account_number.encode())
        # self.account_number = encrypted_account_number
        # self.account_number = FernetFile.fernet_encrypt(self.account_number)

        # При сохранении объекта, генерируем срок годности
        self.expiration_date = datetime.now() + timedelta(days=365 * 4)
        super().save(*args, **kwargs)

    # def get_decrypted_account_number(self):
    #     return FernetFile.fernet_decrypt(self.account_number)
        #str = 'b\'gAAAAABlbM-mjryZfh5yPs7yws_dzbmD2O0jCl5g0wC5osQi1OOmhPvpRgNTH0rm3aRzk1gle8WiWNFkiDDeLjTY6MLu8kmIx7_pLVWuB7mjbQgLKxUkUW0=\''
        # db_account_number = self.account_number
        # clean_data = eval(db_account_number)
        # decrypted_account_number = fernet.decrypt(clean_data).decode()
        #decrypted_account_number = fernet.decrypt(self.account_number).decode()
        # return decrypted_account_number


    # Вывод счетов текущего пользователя опрятным образом, чтобы нельзя было не свой счет отправлять другим
    def __str__(self):
        # Чтобы не забыть что это значит:
        # Ищу все счета, связанные с id пользователя
        count = BankAccounts.objects.filter(user=self.user)
        number = list(count).index(self) + 1
        visible_part = self.account_number[:3] + '*' * (len(self.account_number) - 6) + self.account_number[-3:]
        return f"{number}. {visible_part} ({self.currency})"


# Таблица для переводов (можно сказать что и логирование переводов тоже)
class MoneyTransfer(models.Model):

    sender_id = models.ForeignKey(BankAccounts, related_name='transfers_sent', on_delete=models.CASCADE)
    source_account_number = models.CharField(max_length=20, blank=False, null=False, validators=[MinLengthValidator(16)])

    recipient_id = models.ForeignKey(BankAccounts, related_name='transfers_received', on_delete=models.CASCADE)
    destination_account_number = models.CharField(max_length=20, blank=False, null=False, validators=[MinLengthValidator(16)])

    # Пусть будет 7 цифр, а сумму огрничить в методе
    amount = models.DecimalField(max_digits=7, decimal_places=2, blank=False)
    converted_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=False)

    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.user.username} отправил {self.recipient.user.username}: {self.amount} {self.sender.currency}"