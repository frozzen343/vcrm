from django.shortcuts import render
from django.db.models import Sum
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from tasks.models import Task


def get_time(request):
    time = timezone.now().strftime("%H:%M")
    return JsonResponse({'time': time})


@login_required
def main(request):
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

    return render(request, template_name, context=context)
