from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.core.management import call_command
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.http.response import HttpResponseRedirect
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic import UpdateView, DeleteView, CreateView, ListView
from smtplib import SMTPAuthenticationError
import os
import gzip

from settings.models import Email


class SettingsView(PermissionRequiredMixin, ListView):
    template_name = 'settings/settings_list.html'
    permission_required = 'settings.edit_settings'
    model = Email
    context_object_name = 'email_list'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['messages'] = messages.get_messages(self.request)
        return context


class EmailCreateUpdateView(PermissionRequiredMixin, CreateView, UpdateView):
    permission_required = 'settings.edit_settings'
    template_name = 'settings/email.html'
    model = Email
    success_url = reverse_lazy('settings_list')
    fields = '__all__'

    def get_object(self, queryset=None):
        if self.kwargs.get('pk'):
            return get_object_or_404(self.model, pk=self.kwargs['pk'])
        else:
            return self.model()

    def form_invalid(self, form):
        if 'Нарушено ограничение "sending_unique".' in form.errors['__all__']:
            form.add_error('sending', 'Рассыльная почта '
                                      'может быть только одна')
        return super().form_invalid(form)


class EmailDeleteView(PermissionRequiredMixin, DeleteView):
    permission_required = 'settings.edit_settings'
    model = Email
    success_url = reverse_lazy("settings_list")


def email_test_message(request, email_pk):
    if request.user.has_perm('settings.edit_settings'):
        email = Email.objects.get(pk=email_pk)

        subject = 'VCRM: test mail message'
        message = 'Test mail message is OK'
        try:
            send_mail(subject,
                      message,
                      from_email=f'{email.name} <{email.email}>',
                      recipient_list=[email.email],
                      connection=Email.get_connection())
        except SMTPAuthenticationError as err:
            messages.error(request, f"Ошибка аутентификации SMTP: {err}")
            return HttpResponseRedirect(reverse_lazy('settings_list'))

        messages.success(request, 'Успешная отправка письма')

    return HttpResponseRedirect(reverse_lazy('settings_list'))


def import_backup_view(request):
    if request.method == 'POST' and request.user.has_perm(
            'settings.edit_settings'):
        backup_file = request.FILES.get('backup_file')
        if backup_file:
            compressed_file = (f'{settings.MEDIA_ROOT}/'
                               'temp_backup_compressed.json.gz')
            decompressed_file = f'{settings.MEDIA_ROOT}/temp_backup.json'

            with open(compressed_file, 'wb') as f:
                for chunk in backup_file.chunks():
                    f.write(chunk)

            with gzip.open(compressed_file, 'rb') as f:
                decompressed_data = f.read()

            with open(decompressed_file, 'w') as f:
                f.write(decompressed_data.decode('utf-8'))

            call_command('loaddata', decompressed_file)

            os.remove(compressed_file)
            os.remove(decompressed_file)

            messages.success(request, 'Успешная загрузка бэкапа')

    return HttpResponseRedirect(reverse_lazy('settings_list'))
