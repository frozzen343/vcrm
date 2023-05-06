from django.shortcuts import render
from django.db.models import Sum
from django.utils import timezone
from django.contrib.auth.decorators import login_required

from tasks.models import Task


# def db_backup(request):
#     from django.http import HttpResponse
#     from django.core.management import call_command
#     call_command('loaddata', 'dumped_data.json')  # <
#     call_command('dumpdata --indent=4', 'dumped_data.json')  # >
#     return HttpResponse("Hello")


@login_required
def main(request):
    start = timezone.now()
    template_name = 'main/main.html'

    current_month = timezone.now().month

    context = {
        'count_in_this_month': Task.objects
                                   .filter(performer=request.user,
                                           status='Выполнена',
                                           date_closed__month=current_month)
                                   .count(),

        'hourse_in_this_month': Task.objects
                                    .filter(performer=request.user,
                                            status='Выполнена',
                                            date_closed__month=current_month)
                                    .aggregate(Sum('hours_cost')),

        'count_new_tasks': Task.objects.filter(status='Новая').count(),

        'count_in_progress': Task.objects
                                 .filter(status='В работе',
                                         performer=request.user)
                                 .count(),
    }

    context['time'] = timezone.now() - start

    return render(request, template_name, context=context)
