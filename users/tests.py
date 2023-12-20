from django.contrib.messages import get_messages
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from datetime import date

# Create your tests here.
from django.urls import reverse

from .forms import UserCreationForm, RegistrationForm, LoginForm
from .models import Users, Documents

# для получения класса модели текущего пользователя
User = get_user_model()


class UserCreationFormTest(TestCase):
    def test_valid_userCreationForm(self):
        form_data = {
            'username': 'testuser',
            'name': 'Kira',
            'surname': 'Sadovskaya',
            'email': 'kira@gmail.com',
            'password1': 'testpassword123',
            'password2': 'testpassword123',
            'document_type': 'passport',
            'document_number': 'AB1234567',
            'identification_number': 'ABC125GH147LMN',
            'expiry_date': date(2023, 12, 31),
            'date_of_birth': date(1990, 1, 1),
            'issued_by': 'ROVD',
            'issuing_authority_code': '512',
            'place_of_birth': 'Minsk',
        }
        form = UserCreationForm(data=form_data)
        self.assertTrue(form.is_valid())

    # подтверждение пароля другой
    def test_invalid_userCreationForm(self):
        form_data = {
            'username': 'testuser',
            'name': 'Kira',
            'surname': 'Sadovskaya',
            'email': 'kira@gmail.com',
            'password1': 'testpassword123',
            'password2': 'differentpassword',
            'document_type': 'passport',
            'document_number': 'AB1234567',
            'identification_number': 'ABC125GH147LMN',
            'expiry_date': date(2023, 12, 31),
            'date_of_birth': date(1990, 1, 1),
            'issued_by': 'ROVD',
            'issuing_authority_code': '512',
            'place_of_birth': 'Minsk',
        }
        form = UserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)
        self.assertIn('Введенные пароли не совпадают.', form.errors['password2'])

    def test_invalidDocumentNumber_userCreationForm(self):
        form_data = {
            'username': 'testuser',
            'name': 'Kira',
            'surname': 'Sadovskaya',
            'email': 'kira@gmail.com',
            'password1': 'testpassword123',
            'password2': 'testpassword123',
            'document_type': 'passport',
            'document_number': 'ss1234567',
            'identification_number': 'ABC125GH147LMN',
            'expiry_date': date(2023, 12, 31),
            'date_of_birth': date(1990, 1, 1),
            'issued_by': 'ROVD',
            'issuing_authority_code': '512',
            'place_of_birth': 'Minsk',
        }

        # в общем, сначала происходит переход на представление регистрации, накидывается тестовые данные и вытягивается результат
        url = reverse('registration')
        response = self.client.post(url, form_data)

        messages = [m.message for m in get_messages(response.wsgi_request)]
        form = UserCreationForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertIn('Введите корректные данные. Номер документа должен состоять из 2 заглавных английских букв и 7 цифр', messages)

    def test_invalidExpiryDate_userCreationForm(self):
        form_data = {
            'username': 'testuser',
            'name': 'Kira',
            'surname': 'Sadovskaya',
            'email': 'kira@gmail.com',
            'password1': 'testpassword123',
            'password2': 'testpassword123',
            'document_type': 'passport',
            'document_number': 'AB1234567',
            'identification_number': 'ABC125GH147LMN',
            'expiry_date': date(2022, 12, 4),
            'date_of_birth': date(1990, 1, 1),
            'issued_by': 'ROVD',
            'issuing_authority_code': '512',
            'place_of_birth': 'Minsk',
        }

        url = reverse('registration')
        response = self.client.post(url, form_data)

        messages = [m.message for m in get_messages(response.wsgi_request)]
        form = UserCreationForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertIn('Срок вашей документа закончился - мы не можем регистрировать вас!', messages)


class ViewsAuthenticatedUserTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')

        self.document = Documents.objects.create(
            user=self.user,
            document_type='passport',
            document_number='AB1234567',
            identification_number='ABCDEFGHIJKLMN',
            expiry_date=date(2023, 12, 31),
            date_of_birth=date(1990, 1, 1),
            issued_by='Some Authority',
            issuing_authority_code='12345',
            place_of_birth='City',
        )

        self.client = Client()

    # проверка, что авторизованный пользователь может перемещаться по внутренним вкладкам
    def test_authenticated_user_home_page(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('bankaccount'))
        self.assertEqual(response.status_code, 200)
        self.client.logout()

    def test_registration_view(self):
        response = self.client.get(reverse('registration'))
        self.assertEqual(response.status_code, 200)

    def test_register_view_post_request(self):
        response = self.client.post(reverse('registration'), {
            'username': 'newuser',
            'name': 'John',
            'surname': 'Doe',
            'email': 'newuser@example.com',
            'password1': 'testpassword123',
            'password2': 'testpassword123',
            'document_type': 'passport',
            'document_number': 'AB1234567',
            'identification_number': 'ABCDEFGHIJKLMN',
            'expiry_date': date(2023, 12, 31),
            'date_of_birth': date(1990, 1, 1),
            'issued_by': 'ROVD',
            'issuing_authority_code': '12345',
            'place_of_birth': 'Minsk',
        })
        self.assertEqual(response.status_code, 302)


class ViewsUnauthentificatedUserTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_home_page_view_for_unauthenticated_user(self):
        response = self.client.get(reverse('bankaccount'))
        expected_redirect_url = reverse('Home') + '?next=' + reverse('bankaccount')
        self.assertRedirects(response, expected_redirect_url)
