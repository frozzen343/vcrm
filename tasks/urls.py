from django.urls import path

import tasks.views as views
import tasks.views_api as views_api


urlpatterns = [
    path('list/', views.TaskListView.as_view(), name='task_list'),
    path('create/', views.TaskCreateView.as_view(), name='task_create'),
    path('edit/<int:pk>', views.TaskEditView.as_view(), name='task_edit'),

    path('api/v1/task_list', views_api.TaskListAPIView.as_view(),
         name='api_task_list'),
]
