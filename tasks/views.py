from django.views.generic import TemplateView


class TaskListView(TemplateView):
    template_name = 'tasks/task_list.html'


class TaskCreateView(TemplateView):
    template_name = 'tasks/task_create.html'


class TaskEditView(TemplateView):
    template_name = 'tasks/task_edit.html'
