from django.shortcuts import render
from django.db.models.functions import TruncMonth
from django.db.models import Sum, Count
from django.core.exceptions import PermissionDenied
from django.views.generic import TemplateView

from tasks.models import Task


def main_reports(request):
    template_name = 'reports/main_reports.html'

    context = {
        'hours_per_month': Task.objects
                               .filter(performer=request.user,
                                       status='Выполнена')
                               .annotate(month=TruncMonth('date_closed'))
                               .values('month')
                               .annotate(c=Sum('hours_cost')),

        'count_done_per_month': Task.objects
                                    .filter(performer=request.user,
                                            status='Выполнена')
                                    .annotate(month=TruncMonth('date_closed'))
                                    .values('month')
                                    .annotate(c=Count('id')),

        'new_tasks_per_month': Task.objects
                                   .annotate(month=TruncMonth('date_created'))
                                   .values('month')
                                   .annotate(c=Count('id')),

        'done_tasks_per_month': Task.objects
                                    .filter(date_closed__isnull=False)
                                    .annotate(month=TruncMonth('date_closed'))
                                    .values('month')
                                    .annotate(c=Count('id')),
    }

    return render(request, template_name, context=context)


class HoursReportView(TemplateView):
    template_name = 'reports/hours_reports.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.has_perm('perms.view_users_report'):
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class TaskListReportView(TemplateView):
    template_name = 'reports/report_task_list.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.has_perm('perms.view_users_report'):
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)
