from django.urls import reverse_lazy
from django.utils import timezone
from django.http.response import HttpResponseRedirect
from django.views.generic.edit import UpdateView, CreateView
from django_filters.views import FilterView

from clients.models import Contact
from tasks.models import Task, Comment
from tasks.filters import TaskFilter
from tasks.forms import CommentEditForm


def add_comment(**params):
    comment = Comment(**params)
    comment.save()


def comment_if_changes(task: object, user: object, fields: list):
    if 'hours_cost' in fields:
        comment = (
            f'<p>Пользователь <b>{user.first_name} {user.last_name}</b> '
            f'изменил трудозатраты на <b>{task.hours_cost}</b></p>')
        add_comment(task=task, comment=comment)

    if 'status' in fields:
        comment = (
            f'<p>Пользователь <b>{user.first_name} {user.last_name}</b> '
            f'присвоил статус задачи <b>{task.status}</b></p>')
        add_comment(task=task, comment=comment)

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
        add_comment(task=task, comment=comment)


class TaskListView(FilterView):
    template_name = 'tasks/task_list.html'
    model = Task
    context_object_name = 'tasks'
    paginate_by = 10
    filterset_class = TaskFilter
    ordering = ['-date_created']


class TaskCreateView(CreateView):
    template_name = 'tasks/task_create.html'
    model = Task
    success_url = reverse_lazy('task_list')
    fields = ['title',
              'performer',
              'status',
              'hours_cost',
              'contacts', 'client',
              'fire', 'drive',
              'description']

    def get_initial(self):
        return {'performer': self.request.user}

    def form_valid(self, form):
        comment = (f'Пользователь <b>{self.request.user.first_name} '
                   f'{self.request.user.last_name}</b> создал задачу')
        form.save()
        add_comment(task=form.instance, comment=comment)
        return super().form_valid(form)


class TaskEditView(UpdateView):
    template_name = 'tasks/task_edit.html'
    model = Task
    extra_context = {'contacts': Contact.objects.values_list('contact',
                                                             flat=True)}
    second_form_class = CommentEditForm
    fields = ['status',
              'hours_cost',
              'performer',
              'contacts', 'client',
              'fire', 'drive',
              'description']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context["form2"] = self.second_form_class(self.request.POST)
        else:
            context["form2"] = self.second_form_class()

        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
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
            if button == 'Выполнено':
                task.status = 'Выполнена'
                task.date_closed = timezone.localtime()
            if button == 'Отложено':
                task.status = 'Отложена'
            if button == 'Не задача':
                task.status = 'Не задача'
            task.save()
            return HttpResponseRedirect(self.get_success_url())
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        if form.has_changed():
            comment_if_changes(self.object,
                               self.request.user,
                               form.changed_data)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("task_edit", kwargs={'pk': self.kwargs['pk']})
