from django.utils import timezone
from django.db.models import Sum
import pandas as pd

from tasks.models import Task


def make_hours_table(month=timezone.now().month, year=timezone.now().year):
    tasks = Task.objects \
            .filter(date_closed__month=month,
                    date_closed__year=year,
                    performer__isnull=False,
                    status='Выполнена') \
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
