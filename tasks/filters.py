import django_filters

from tasks.models import Task
from users.models import User


class TaskFilter(django_filters.FilterSet):
    performer = django_filters.ModelChoiceFilter(
        queryset=User.objects.filter(is_active=True))

    class Meta:
        model = Task
        fields = ['title', 'performer', 'status']
