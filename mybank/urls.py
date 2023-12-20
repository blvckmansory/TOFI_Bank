from django.conf.urls.static import static
from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

from bankaccount.views import *
from loans.views import *
from users.views import *

urlpatterns = [
    path('admin/', admin.site.urls),

    # чтобы не писать каждый раз ссылку, то делаем для каждого приложения отдельный файл urls
    path('bankaccount/', include('bankaccount.urls')),
    path('loans/', include('loans.urls')),
    path('users/', include('users.urls')),

    # Первый вариант являктся просто как представление вида и поэтмоу я не смогу передавать параметры и нужно
    # во views.py сделать метод, который и нужен для реализации того что хочу
    # path('', TemplateView.as_view(template_name='Home.html'), name='Home'),
    path('', home_page, name='Home'),
]

# if settings.DEBUG:
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


# Специальный обработчик для 404, handler вызывается каждый раз когда ошибка будет
handler404 = pageNotFound
