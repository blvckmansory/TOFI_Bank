from django.urls import path

from bankaccount import views
from bankaccount.views import *
from users.views import *

urlpatterns = [
    path('bankaccounts/', not_logged_in(bankaccount_index), name='bankaccount'),
    path('money_transfer/', not_logged_in(money_transfer_index), name='money_transfer'),
    # path('money_transfer/', not_logged_in(money_transfer_info), name='money_transfer_info'),
    path('money_transfer_history/', not_logged_in(views.money_transfer_history), name='money_transfer_history'),

    # если будем присваивать для каждой категории отдельный id
    path('categories/<int:categoryID>/', categories),
]
