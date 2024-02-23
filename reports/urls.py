from django.urls import path

import reports.views as views
import reports.views_api as views_api


urlpatterns = [
    path('main', views.main_reports, name='main_reports'),
    path('hours', views.HoursReportView.as_view(), name='hours_reports'),
    path('task_list', views.TaskListReportView.as_view(),
         name='report_task_list'),

    path('api/v1/hours_report', views_api.HoursReportAPIView.as_view(),
         name='api_hours_report'),
    path('api/v1/to_excel', views_api.DownloadExcelAPIView.as_view(),
         name='api_to_excel'),
]
