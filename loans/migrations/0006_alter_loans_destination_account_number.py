# Generated by Django 4.2.7 on 2023-12-04 07:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('loans', '0005_alter_loans_loan_number'),
    ]

    operations = [
        migrations.AlterField(
            model_name='loans',
            name='destination_account_number',
            field=models.CharField(max_length=255, null=True),
        ),
    ]
