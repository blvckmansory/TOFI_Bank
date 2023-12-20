# данный файл создан для тогда чтобы в методах в views не дублировать кода
# по типу users = Users.objects.all() - получения списка всех пользователей

from django import template
from users.models import *

register = template.Library()


# Превращаем функцию в тег
@register.simple_tag(name='getUsers')
def get_user():
    return Users.objects.all()
