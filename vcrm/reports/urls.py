from django.urls import path

from reports.views import main_reports, hours_reports


urlpatterns = [
    path('main', main_reports, name='main_reports'),
    path('hours', hours_reports, name='hours_reports'),
]
