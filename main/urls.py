from django.urls import path

from main.views import main, get_time


urlpatterns = [
    path('', main, name='main'),
    path('get_time', get_time, name='get_time'),
]
