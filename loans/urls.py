from django.urls import path
from loans.views import *
from users.views import *

urlpatterns = [
    path('apply-loan/', not_logged_in(apply_loan_index), name='apply_for_loan'),
    path('payments/', not_logged_in(payments_index), name='payments'),
]
