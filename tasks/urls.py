from django.urls import path

from tasks.views import (TaskListView,
                         TaskCreateView,
                         TaskEditView,)


urlpatterns = [
    path('list/', TaskListView.as_view(), name='task_list'),
    path('create/', TaskCreateView.as_view(), name='task_create'),
    path('edit/<int:pk>', TaskEditView.as_view(), name='task_edit'),
]
