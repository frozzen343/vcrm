from django.urls import reverse_lazy
from django.http.response import HttpResponseRedirect
from django.views.generic.edit import UpdateView, CreateView
from django_filters.views import FilterView
from django.db.models import Q
from django.core.exceptions import PermissionDenied

from clients.models import Contact
from tasks.models import Task, Comment
from tasks.filters import TaskFilter
from tasks.forms import CommentEditForm, TaskCreateForm
from mail.views import send_mail_notice_task


def comment_if_changes(task: object, user: object, fields: list):
    if 'hours_cost' in fields:
        comment = (
            f'<p>Пользователь <b>{user.first_name} {user.last_name}</b> '
            f'изменил трудозатраты на <b>{task.hours_cost}</b></p>')
        Comment.objects.create(task=task, comment=comment)

    if 'status' in fields:
        comment = (
            f'<p>Пользователь <b>{user.first_name} {user.last_name}</b> '
            f'присвоил статус задачи <b>{task.status}</b></p>')
        Comment.objects.create(task=task, comment=comment)

    if 'performer' in fields:
        if task.performer:
            comment = (
                f'<p>Пользователь <b>{user.first_name} {user.last_name}'
                '</b> назначил исполнителя задачи <b>'
                f'{task.performer.first_name} {task.performer.last_name}'
                '</b></p>')
        else:
            comment = (f'<p>Пользователь <b>{user.first_name} {user.last_name}'
                       '</b> убрал исполнителя задачи</p>')
        Comment.objects.create(task=task, comment=comment)


class TaskListView(FilterView):
    template_name = 'tasks/task_list.html'
    model = Task
    context_object_name = 'tasks'
    paginate_by = 10
    filterset_class = TaskFilter
    ordering = ['-date_created']

    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.has_perm('perms.view_other_users_tasks'):
            queryset = queryset.filter(Q(performer=self.request.user) |
                                       Q(performer=None))
        return queryset


class TaskCreateView(CreateView):
    template_name = 'tasks/task_create.html'
    model = Task
    success_url = reverse_lazy('task_list')
    form_class = TaskCreateForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_initial(self):
        return {'performer': self.request.user}

    def form_valid(self, form):
        if not self.request.user.has_perm('perms.change_performer') and \
                form.cleaned_data['performer'] and \
                form.cleaned_data['performer'] != self.request.user:
            raise PermissionDenied

        comment = (f'Пользователь <b>{self.request.user.first_name} '
                   f'{self.request.user.last_name}</b> создал задачу')
        form.save()
        Comment.objects.create(task=form.instance, comment=comment)
        return super().form_valid(form)


class TaskEditView(UpdateView):
    template_name = 'tasks/task_edit.html'
    model = Task
    extra_context = {
        'contacts': Contact.objects.values_list('contact', flat=True),
    }
    second_form_class = CommentEditForm
    fields = ['status',
              'hours_cost',
              'performer',
              'contacts', 'client',
              'fire', 'drive',
              'description']

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()

        if self.object.performer \
            and self.object.performer != request.user \
            and not self.request.user.has_perm(
                    'perms.view_other_users_tasks'):
            raise PermissionDenied()
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = Comment.objects.filter(task=self.object) \
                                             .order_by('-date_created')
        if self.request.POST:
            context["form2"] = self.second_form_class(self.request.POST)
        else:
            context["form2"] = self.second_form_class()

        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        if 'add_comment' not in request.POST \
                and not self.request.user.has_perm('perms.edit_closed_task') \
                and self.object.status == 'Выполнена':
            raise PermissionDenied()

        if 'add_comment' in request.POST:
            form_comment = self.second_form_class(request.POST)
            if form_comment.is_valid():
                comment = form_comment.save(commit=False)
                comment.performer = request.user
                comment.task = self.object
                comment.save()
            return HttpResponseRedirect(self.get_success_url())

        elif 'edit_buttons' in request.POST:
            task = self.object
            button = request.POST.get('edit_buttons')
            if button == 'Принять':
                task.status = 'В работе'
                task.performer = request.user
                comment_if_changes(
                    task=task, user=request.user, fields=['status'])
                if 'notice_take' in request.POST:
                    send_mail_notice_task(task, 'mail/take_task.html')

            if button == 'Выполнено':
                task.status = 'Выполнена'
                comment_if_changes(
                    task=task, user=request.user, fields=['status'])
                if 'notice_done' in request.POST:
                    send_mail_notice_task(task, 'mail/take_done.html')

            if button == 'Отложено':
                task.status = 'Отложена'
                comment_if_changes(
                    task=task, user=request.user, fields=['status'])

            if button == 'Не задача':
                task.status = 'Не задача'
                comment_if_changes(
                    task=task, user=request.user, fields=['status'])

            task.save()
            return HttpResponseRedirect(self.get_success_url())
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        if not self.request.user.has_perm('perms.change_performer') and \
                form.cleaned_data['performer'] and \
                form.cleaned_data['performer'] != self.request.user:
            raise PermissionDenied
        if form.has_changed():
            comment_if_changes(self.object,
                               self.request.user,
                               form.changed_data)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("task_edit", kwargs={'pk': self.kwargs['pk']})
