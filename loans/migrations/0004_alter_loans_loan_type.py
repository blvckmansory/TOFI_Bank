# Generated by Django 4.2.7 on 2023-11-21 07:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('loans', '0003_loans_destination_account_number'),
    ]

    operations = [
        migrations.AlterField(
            model_name='loans',
            name='loan_type',
            field=models.CharField(choices=[('Consumer_loan', 'Потребительский кредит'), ('Mortgage_loan', 'Ипотечный кредит'), ('Auto_loan', 'Автокредит')], max_length=100),
        ),
    ]
