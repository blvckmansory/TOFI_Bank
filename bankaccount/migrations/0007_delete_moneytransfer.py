# Generated by Django 4.2.7 on 2023-11-14 10:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bankaccount', '0006_moneytransfer'),
    ]

    operations = [
        migrations.DeleteModel(
            name='MoneyTransfer',
        ),
    ]
