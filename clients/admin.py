from django.contrib import admin
from .models import Client, Contact


class ContactsInline(admin.StackedInline):
    model = Contact
    extra = 0


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('name', 'web_site', 'phone', 'address', 'is_active',
                    'date_created')
    list_filter = ('is_active', 'date_created')
    search_fields = ('name', 'phone', 'address', 'description')
    ordering = ['name']
    inlines = [ContactsInline]


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('contact', 'fio', 'client', 'last_activity')
    list_filter = ('last_activity',)
    search_fields = ('contact', 'fio', 'client__name')
