from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import ListAPIView
from datetime import datetime

from tasks.models import Task
from tasks.serializers import TaskListSerializer


class TaskListAPIView(ListAPIView):
    """
    Task list view with filters
    """
    queryset = Task.objects.order_by('-date_created').all()
    serializer_class = TaskListSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['performer', 'status', 'client_id',]

    def get_queryset(self):
        queryset = super().get_queryset()
        full_month = self.request.query_params.get('full_month')
        if full_month:
            full_month = datetime.strptime(full_month, '%Y-%m-%d')
            full_month = full_month.replace(day=1)
            queryset = (queryset
                        .filter(date_closed__month=full_month.month,
                                date_closed__year=full_month.year)
                        .order_by('-date_closed'))

        status = self.request.query_params.get('status', None)
        if status == 'Новая':
            return queryset.filter(performer=None)

        if not self.request.user.has_perm('perms.view_other_users_tasks'):
            queryset = queryset.filter(performer=self.request.user)
        return queryset
