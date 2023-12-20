from datetime import date

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone

from users.forms import UserCreationForm
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth import authenticate, login, logout
from mybank.FernetFile import *
import re

from users.models import Users, Documents

menu = [{'title': "О нас", 'url_name': 'About'},
        ]


# Будет ошибкой, если пытаться использовать имена ссылок, которых еще нет, поэтому шаблон не отобразится и будет ошибкой
# добавить ссылки нужно будет в users/urls
def home_page(request):

    menu = [
        # {'title': 'Личный кабинет', 'url_name': 'account_settings'},
        {'title': 'Просмотр счетов', 'url_name': 'bankaccount'},
        {'title': 'Денежные переводы', 'url_name': 'money_transfer'},
        {'title': 'Оформление кредита', 'url_name': 'apply_for_loan'},
        {'title': 'Платежи', 'url_name': 'payments'},
        {'title': 'История транзакций', 'url_name': 'money_transfer_history'},
    ]

    context = {
        'title': 'Домашняя страница',
        'menu': menu,
    }
    return render(request, 'user/Home.html', context)


def about_us_page(request):
    return render(request, 'user/about.html', {'title': 'О нас'})


# Класс регистрации
class Register(View):
    template_name = 'registration/registration.html'

    def get(self, request):
        context = {
            'form': UserCreationForm(),
            'title': 'Страница регистрации'
        }
        return render(request, self.template_name, context)

    def post(self, request):
        if request.user.is_authenticated:
            return redirect('Home')

        form = UserCreationForm(request.POST)

        if form.is_valid():

            # проверка номера документа
            document_number = form.cleaned_data['document_number']
            regex = r'^[A-Z]{2}\d{7}$'
            if not re.match(regex, document_number):
                messages.error(request, 'Введите корректные данные. Номер документа должен состоять из 2 заглавных английских букв и 7 цифр')

                context = {
                    'form': form,
                }
                return render(request, self.template_name, context)

            # проверка идентификационного номера
            identification_number = form.cleaned_data['identification_number']
            if len(identification_number) != 14:
                messages.error(request,
                               'Введите корректные данные идентификационного номера.')
                context = {
                    'form': form,
                }
                return render(request, self.template_name, context)
            else:
                if not identification_number.isupper():
                    messages.error(request, 'Идентификационный номер должен содержать только заглавные буквы.')

                    context = {
                        'form': form,
                    }
                    return render(request, self.template_name, context)


            # проверка даты срока документа
            expiry_date = form.cleaned_data['expiry_date']
            today = date.today()
            if expiry_date < today:
                messages.error(request, 'Срок вашей документа закончился - мы не можем регистрировать вас!')

                context = {
                    'form': form,
                }
                return render(request, self.template_name, context)

            # проверка возраста пользователя
            date_of_birth = form.cleaned_data['date_of_birth']
            age = today.year - date_of_birth.year - ((today.month, today.day) < (date_of_birth.month, date_of_birth.day))
            if age < 14:
                messages.error(request, 'Регистрация доступна только для пользователей старше 14 лет.')

                context = {
                    'form': form,
                }
                return render(request, self.template_name, context)

            # Сначала нужно сохранить пользователя, а потом по его id уже сохранить его документы
            user = form.save()
            # Теперь получаем пользователя из базы данных
            user = get_object_or_404(Users, id=user.id)
            # Сохраняем данные о документах
            document = Documents.objects.create(
                user=user,
                document_type=form.cleaned_data['document_type'],
                # Нужна логика с проверкой уже существующего номера документа (можно ли создавать нексколько аккаунтов для одного документа или нет)
                document_number=fernet_encrypt(form.cleaned_data['document_number']),
                identification_number=fernet_encrypt(form.cleaned_data['identification_number']),
                expiry_date=form.cleaned_data['expiry_date'],
                date_of_birth=form.cleaned_data['date_of_birth'],
                issued_by=form.cleaned_data['issued_by'],
                issuing_authority_code=form.cleaned_data['issuing_authority_code'],
                place_of_birth=form.cleaned_data['place_of_birth'],
            )

            document.save()

            # form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect('Home')

        context = {
            'form': form,
        }
        return render(request, self.template_name, context)



# Прописываем декоратор, который уже не позволит авторизованным пользователям вернуться на страницу входа, регистрации и тд
def logged_in(view_func):
    decorated_view = user_passes_test(lambda user: not user.is_authenticated, login_url='Home')
    return decorated_view(view_func)


# Тут наоборот, чтобы неавторизоавнные не могли по url бегать по страницам
def not_logged_in(view_func):
    decorated_view = user_passes_test(lambda user: user.is_authenticated, login_url='Home')
    return decorated_view(view_func)


# Тут восстановление пароля, но пока что траблы
class Reset_password(View):
    template_name = 'registration/password_reset_form.html'

    def get(self, request):
        return render(request, self.template_name)
