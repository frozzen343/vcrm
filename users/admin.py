from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from users.models import User


class UserPanelAdmin(UserAdmin):
    fieldsets = (
        (None, {"fields": ("first_name", "last_name", 'email', 'password',
                           'is_active', 'background', 'avatar',
                           'notify_new_tasks', 'is_superuser', 'is_staff',
                           'groups')}),
    )
    add_fieldsets = (
        (None, {"classes": ("wide",),
                "fields": ("first_name", "last_name", "email",
                           "password1", "password2",
                           "is_superuser", "is_staff", 'groups'),
                },),
    )
    list_display = ['id', 'first_name', 'last_name',
                    'email', 'is_active']
    list_filter = ['is_active', 'groups']
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ['id']


admin.site.register(User, UserPanelAdmin)
