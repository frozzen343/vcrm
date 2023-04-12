from django.shortcuts import render
from django.db.models.functions import TruncMonth
from django.db.models import Sum, Count
from django.http import HttpResponse
from django.utils import timezone
from io import BytesIO
import pandas as pd

from tasks.models import Task
from reports.forms import HoursReportForm


def make_hours_table(month=timezone.now().month, year=timezone.now().year):
    tasks = Task.objects \
            .filter(date_created__month=month,
                    date_created__year=year,
                    performer__isnull=False) \
            .values('performer__last_name', 'client__name') \
            .annotate(hours=Sum('hours_cost')) \
            .order_by('client')

    if not tasks:
        return None

    df = pd.DataFrame(tasks)
    df = df.fillna('-')
    df = df.pivot_table(values='hours',
                        index='client__name',
                        columns='performer__last_name',
                        fill_value=0)
    df.loc['Итого'] = df.sum(numeric_only=True, axis=0)
    df.loc[:, 'Итого'] = df.sum(numeric_only=True, axis=1)

    df.columns.name = None
    df.index.name = None

    return df


def download_excel(month=timezone.now().month, year=timezone.now().year):
    df = make_hours_table(month, year)

    if df is not None:
        with BytesIO() as b:
            with pd.ExcelWriter(b) as writer:
                df.to_excel(writer, sheet_name="Расчет часов")

            filename = f'hours_report_{month}_{year}.xlsx'

            res = HttpResponse(
                b.getvalue(),
                content_type='application/vnd.openxmlformats-'
                             'officedocument.spreadsheetml.sheet'
            )
            res['Content-Disposition'] = f'attachment; filename={filename}'
            return res
    else:
        return HttpResponse('<p>Данных ещё нет<p>')


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


def hours_reports(request):
    template_name = 'reports/hours_reports.html'

    if request.method == 'POST':
        form = HoursReportForm(request.POST)
        if form.is_valid():
            month = form.cleaned_data['month']
            year = form.cleaned_data['year']
            if 'to_excel' in request.POST:
                return download_excel(month, year)
    else:
        form = HoursReportForm()
        month = timezone.now().month
        year = timezone.now().year

    df = make_hours_table(month, year)

    context = {
        'form': form,
        'table': df.to_html() if df is not None else '<p>Данных ещё нет<p>',
    }

    return render(request, template_name, context=context)
