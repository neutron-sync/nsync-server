from django.contrib import admin

from django.contrib.auth.admin import UserAdmin

from nsync_server.account.models import User


@admin.register(User)
class UserAdmin(UserAdmin):
  list_display = ('username', 'email', 'name', 'is_active', 'is_staff', 'is_superuser', 'last_login')
  list_filter = ('last_login', 'is_staff')
