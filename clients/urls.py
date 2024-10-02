from django.urls import path, re_path

import clients.views_api as views_api
from clients.views import (ClientListView,
                           ClientCreateView,
                           ClientEditView,
                           ClientDeleteView,
                           ContactListView,
                           ContactCreateView,
                           ContactEditView,
                           ContactDeleteView)


urlpatterns = [
    path('list/', ClientListView.as_view(), name='client_list'),
    path('create/', ClientCreateView.as_view(), name='client_create'),
    path('edit/<int:pk>', ClientEditView.as_view(), name='client_edit'),
    path('del/<int:pk>', ClientDeleteView.as_view(), name='client_del'),
    path('edit/<int:fk>/contacts/',
         ContactListView.as_view(),
         name='contact_list'),
    re_path(r'^edit/(?P<fk>\d+)/contacts/create/(?P<contact>.*)?$',
            ContactCreateView.as_view(),
            name='contact_create'),
    path('edit/<int:fk>/contacts/edit/<int:pk>',
         ContactEditView.as_view(),
         name='contact_edit'),
    path('edit/<int:fk>/contacts/del/<int:pk>',
         ContactDeleteView.as_view(),
         name='contact_del'),

    path('api/v1/client_attach', views_api.AttachContactToClient.as_view(),
         name='api_client_attach'),
    path('api/v1/client_list', views_api.ClientListAPIView.as_view(),
         name='api_client_list'),
]
