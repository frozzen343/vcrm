from django.urls import path

from settings.views import SettingsView, EmailCreateUpdateView,\
    EmailDeleteView, email_test_message, import_backup_view

urlpatterns = [
    path('list/', SettingsView.as_view(), name='settings_list'),
    path('email/create/', EmailCreateUpdateView.as_view(), name='email_add'),
    path('email/edit/<int:pk>/', EmailCreateUpdateView.as_view(),
         name='email_edit'),
    path('email/del/<int:pk>/', EmailDeleteView.as_view(), name='email_del'),
    path('email/testmessage/<int:email_pk>/', email_test_message,
         name='email_test'),
    path('import/', import_backup_view, name='import_backup'),
]
