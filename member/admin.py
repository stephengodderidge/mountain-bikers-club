from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import User


class UserInline(admin.StackedInline):
    model = User


class UserAdmin(BaseUserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password', 'is_active', 'is_premium', 'premium_until')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Trails'), {'fields': ('favorite_trails',)}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
        (_('Permissions'), {'fields': ('is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
    )


admin.site.register(User, UserAdmin)
