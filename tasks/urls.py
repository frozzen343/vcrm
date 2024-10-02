from rest_framework.routers import DefaultRouter
from django.urls import path, include

import tasks.views as views
import tasks.views_api as views_api


router = DefaultRouter()
router.register(r'tasks', views_api.TaskViewSet)
router.register(r'comments', views_api.CommentViewSet)


urlpatterns = [
    path('list/', views.TaskListView.as_view(), name='task_list'),
    path('create/', views.TaskCreateView.as_view(), name='task_create'),
    path('edit/<int:pk>', views.TaskEditView.as_view(), name='task_edit'),

    path('api/v1/', include(router.urls)),
]
