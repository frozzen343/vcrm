from django.contrib import admin
from .models import Mail, Attachment


class AttachmentsInline(admin.StackedInline):
    model = Attachment
    extra = 0


@admin.register(Mail)
class MailAdmin(admin.ModelAdmin):
    list_display = ('subject', 'from_name', 'from_email', 'to', 'date')
    list_filter = ('date',)
    search_fields = ('from_name', 'from_email', 'to', 'cc', 'subject')
    readonly_fields = ['id', 'messageid', 'date', 'server_messageid']
    inlines = [AttachmentsInline]

    def has_add_permission(self, request):
        return False
