# Generated by Django 4.2.7 on 2023-11-12 15:48

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Currency',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('currency_code', models.CharField(max_length=3, unique=True)),
                ('currency_name', models.CharField(choices=[('BYN', 'Белорусский рубль'), ('USD', 'Американский доллар'), ('RUB', 'Российский рубль'), ('EUR', 'Евро'), ('CNY', 'Китайский юань')], max_length=50, unique=True)),
                ('exchange_rate_to_byn', models.DecimalField(decimal_places=6, max_digits=10)),
            ],
        ),
        migrations.CreateModel(
            name='BankAccounts',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('account_type', models.CharField(choices=[('checking_account', 'Текущий счет'), ('loan_account', 'Кредитный счет')], max_length=30)),
                ('account_number', models.CharField(max_length=20, unique=True, validators=[django.core.validators.MinLengthValidator(16)])),
                ('balance', models.DecimalField(decimal_places=2, max_digits=10, validators=[django.core.validators.MinValueValidator(0)])),
                ('expiration_date', models.DateField()),
                ('currency', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='bankaccount.currency')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
