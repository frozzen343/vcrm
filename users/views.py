from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.http.response import HttpResponseRedirect
from django.contrib.auth.models import Group
from django.contrib.auth.views import LoginView, PasswordChangeView
from django.contrib.auth.forms import SetPasswordForm, AuthenticationForm
from django.contrib.auth.mixins import (LoginRequiredMixin,
                                        PermissionRequiredMixin)
from django.core.exceptions import PermissionDenied
from django.views.generic import UpdateView, DeleteView, CreateView, ListView

from users.forms import CreateUserForm
from users.models import User


def background(request):
    """save changed background img."""
    if request.method == 'POST':
        img = request.POST.get("img", "none")
        user = request.user
        user.background = img
        user.save()
        return HttpResponseRedirect(reverse_lazy('main'))

    template_name = 'users/background.html'
    return render(request, template_name)


def group_delete(request, user_id, group_id):
    if request.user.has_perm('auth.change_permission'):
        user = get_object_or_404(User, pk=user_id)
        user.groups.remove(group_id)
        success_url = reverse_lazy("user_edit", kwargs={'pk': user_id})
        return HttpResponseRedirect(success_url)
    raise PermissionDenied()


def group_add(request, user_id, group_id):
    if request.user.has_perm('auth.change_permission'):
        user = get_object_or_404(User, pk=user_id)
        user.groups.add(group_id)
        success_url = reverse_lazy("user_edit", kwargs={'pk': user_id})
        return HttpResponseRedirect(success_url)
    raise PermissionDenied()


class UserLoginView(LoginView):
    form_class = AuthenticationForm
    redirect_authenticated_user = True


class UserProfileView(LoginRequiredMixin, UpdateView):
    model = User
    template_name = 'users/profile.html'
    fields = ['first_name', 'last_name',
              'email',
              'avatar',
              'notify_new_tasks']

    def dispatch(self, request, *args, **kwargs):
        if kwargs['pk'] != request.user.id:
            raise PermissionDenied()
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy("profile", kwargs={'pk': self.request.user.pk})


class UserChangePass(LoginRequiredMixin, PasswordChangeView):
    template_name = "users/user_change_pass.html"
    form_class = SetPasswordForm
    success_url = reverse_lazy("main")

    def dispatch(self, request, *args, **kwargs):
        if (kwargs['pk'] != request.user.id and
                not request.user.has_perm('users.change_user')):
            raise PermissionDenied()
        self.user = get_object_or_404(User, pk=kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.user
        return kwargs


class UserCreateView(PermissionRequiredMixin, CreateView):
    permission_required = 'users.add_user'
    model = User
    template_name = 'users/user_create.html'
    success_url = reverse_lazy("user_list")
    form_class = CreateUserForm


class UserListView(PermissionRequiredMixin, ListView):
    permission_required = 'users.view_user'
    model = User
    context_object_name = 'users'


class UserEditView(PermissionRequiredMixin, UpdateView):
    permission_required = 'users.change_user'
    model = User
    context_object_name = 'user_ed'
    template_name = 'users/user_edit.html'
    fields = ['first_name', 'last_name', 'email', 'is_active']
    success_url = reverse_lazy("user_list")
    extra_context = {'groups': Group.objects.all()}


class UserDeleteView(PermissionRequiredMixin, DeleteView):
    permission_required = 'users.delete_user'
    model = User
    success_url = reverse_lazy("user_list")
