from django.contrib import admin

# Register your models here.

from .models import *


class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'surname', 'email', 'password')
    list_display_links = ('id', 'name')
    search_fields = ('name',)


admin.site.register(Users, UserAdmin)
# admin.site.register(Security)
admin.site.register(Documents)
