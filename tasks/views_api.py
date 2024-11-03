from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import viewsets, status
from datetime import datetime

from tasks.models import Task, Comment
from mail.utils import send_mail_notice_task
from tasks.serializers import (TaskSerializer, TaskCreateSerializer,
                               TaskDetailSerializer, CommentSerializer)


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.order_by('-date_created').all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['performer', 'client_id', ]

    # def perform_create(self, serializer):
    #     instance = serializer.save()
    #     user_first_name = self.request.user.first_name
    #     user_last_name = self.request.user.last_name
    #     comment = (f'<p>Пользователь <b>{user_first_name} {user_last_name}
    #               '</b> создал задачу</p>')
    #     Comment.objects.create(task=instance, comment=comment)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data,
                                         partial=partial)

        task_performer = request.data.get('performer', None)
        task_status = request.data.get('status', None)

        if task_status and (instance.status == 'Новая' or
                            instance.status == 'Не задача'):
            instance.performer = request.user

        if (not self.request.user.has_perm('perms.change_performer')
                and task_performer):
            raise PermissionDenied()

        if task_status == 'Выполнена' and not instance.client:
            return Response(
                {"error": "Неправильный аргумент: поле client не предоставлено."},
                status=status.HTTP_400_BAD_REQUEST
            )


        if task_performer == '':
            instance.status = 'Новая'

        if task_performer and not task_status and instance.status == 'Новая':
            instance.status = 'В работе'

        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        mail_notice = request.data.get('mail_notice', None) == 'true'
        if mail_notice:
            if serializer.data['status'] == 'В работе':
                send_mail_notice_task(instance, 'mail/take_task.html')
            elif serializer.data['status'] == 'Выполнена':
                send_mail_notice_task(instance, 'mail/take_done.html')

        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    def get_serializer_class(self):
        if self.action == 'create':
            return TaskCreateSerializer
        elif self.action == 'retrieve':
            return TaskDetailSerializer
        return TaskSerializer

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
            return queryset.filter(Q(performer=None) | Q(status='Новая'))
        elif status:
            queryset = queryset.filter(status=status)
        if status == 'Выполнена':
            queryset = queryset.order_by('-date_closed')

        if not self.request.user.has_perm('perms.view_other_users_tasks'):
            queryset = queryset.filter(Q(performer=self.request.user)
                                       | Q(performer=None))
        return queryset


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.order_by('-date_created').all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['comment_type', 'task']

    def perform_create(self, serializer):
        serializer.save(performer=self.request.user)
