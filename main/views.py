from django.shortcuts import render
from django.db.models import Sum
from django.utils import timezone
from django.contrib.auth.decorators import login_required

from tasks.models import Task


def handler400(request, exception):
    return render(request, 'errors/400.html', status=400)


def handler403(request, exception):
    return render(request, 'errors/403.html', status=403)


def handler404(request, exception):
    return render(request, 'errors/404.html', status=404)


def handler500(request):
    return render(request, 'errors/500.html', status=500)


@login_required
def main(request):
    template_name = 'main/main.html'

    current_month = timezone.now().month
    current_year = timezone.now().year

    context = {
        'count_in_this_month': Task.objects
                                   .filter(performer=request.user,
                                           status='Выполнена',
                                           date_closed__month=current_month,
                                           date_closed__year=current_year)
                                   .count(),
        'hourse_in_this_month': Task.objects
                                    .filter(performer=request.user,
                                            status='Выполнена',
                                            date_closed__month=current_month,
                                            date_closed__year=current_year)
                                    .aggregate(Sum('hours_cost')),
        'count_new_tasks': Task.objects.filter(status='Новая').count(),
        'count_in_progress': Task.objects
                                 .filter(status='В работе',
                                         performer=request.user)
                                 .count(),
    }

    return render(request, template_name, context=context)
