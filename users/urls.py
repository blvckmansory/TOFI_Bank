
from django.contrib.auth import views as auth_views
from django.urls import path, include
from django.views.generic import TemplateView

from users.views import *

urlpatterns = [
    path('login/', logged_in(auth_views.LoginView.as_view()), name='login'),
    path('', include('django.contrib.auth.urls')),
    path('register/', logged_in(Register.as_view()), name='registration'),
    path('password_reset/', logged_in(Reset_password.as_view()), name='password_reset'),
    path('about_us/', not_logged_in(about_us_page), name='About'),
]
