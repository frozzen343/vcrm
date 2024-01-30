from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import ListAPIView
from django.db.models import Q

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
    filterset_fields = ['performer', 'status']

    def get_queryset(self):
        queryset = super().get_queryset()
        status = self.request.query_params.get('status', None)
        performer_param = self.request.query_params.get('performer', None)
        if not performer_param and status != 'Новая':
            return queryset.filter(performer=self.request.user)

        if not self.request.user.has_perm('perms.view_other_users_tasks'):
            queryset = queryset.filter(Q(performer=self.request.user) |
                                       Q(performer=None))
        return queryset
