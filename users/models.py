from django.db import models
from django.urls import reverse
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinLengthValidator, EmailValidator


# Пользователи
# не прописывается id поскольку в классе Model уже автоматически оно есть
class Users(AbstractUser):
    name = models.CharField(max_length=25, blank=False, null=False, validators=[MinLengthValidator(2)])
    surname = models.CharField(max_length=40, blank=False, null=False, validators=[MinLengthValidator(2)])
    patronimyc = models.CharField(max_length=40, blank=True)
    password = models.CharField(max_length=128, blank=False, null=False)

    # Готовый метод для валидации правильности введения почты, хотя нужно будет сделать это in real time
    email = models.EmailField(unique=True, blank=False, null=False, validators=[EmailValidator()])
    last_confirmation_code_sent = models.DateTimeField(null=True, blank=True)

    # Добавляем related_name для избежания конфликта имени
    groups = models.ManyToManyField('auth.Group', related_name='custom_user_groups', blank=True)
    user_permissions = models.ManyToManyField('auth.Permission', related_name='custom_user_user_permissions',
                                              blank=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('user', kwargs={'user_id': self.pk})

    class Meta:
        verbose_name = "Пользователи"
        # Чтобы убрать s на конце
        verbose_name_plural = "Пользователи"
        ordering = ['-id']


# Документы данные
class Documents(models.Model):
    Documents_TYPES = (
        ('passport', 'Паспорт'),
        ('green_card', 'Вид на жительство'),
        ('foreign_passport', 'Заграничный паспорт'),
    )
    user = models.OneToOneField(Users, on_delete=models.CASCADE)
    document_type = models.CharField(max_length=30, choices=Documents_TYPES)
    document_number = models.CharField(max_length=255, blank=False, null=False, unique=True,
                                       validators=[MinLengthValidator(8)])
    identification_number = models.CharField(max_length=255, blank=False, null=False, unique=True, validators=[MinLengthValidator(14)])
    expiry_date = models.DateField()
    date_of_birth = models.DateField()
    issued_by = models.CharField(max_length=100)
    issuing_authority_code = models.CharField(max_length=10)
    place_of_birth = models.CharField(max_length=100)

    class Meta:
        verbose_name = "Документы"
        verbose_name_plural = "Документы"


