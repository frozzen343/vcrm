from django.urls import path

import mail.views_api as views_api


urlpatterns = [
    path('api/v1/mail_get', views_api.YourApiView.as_view(),
         name='api_mail_get'),
]
