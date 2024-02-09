from django.urls import path

import main.views as views
import main.views_api as views_api


urlpatterns = [
    path('', views.main, name='main'),

    path('api/v1/get_time', views_api.GetTimeAPIView.as_view(),
         name='api_get_time'),
]
