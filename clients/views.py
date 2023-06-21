from django.views.generic import ListView, UpdateView, CreateView, DeleteView
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.exceptions import PermissionDenied
from django.urls import reverse_lazy

from clients.models import Client, Contact


class ClientListView(ListView):
    model = Client
    context_object_name = 'clients'
    paginate_by = 10
    ordering = ['name']


class ClientCreateView(PermissionRequiredMixin, CreateView):
    permission_required = 'clients.add_client'
    template_name = 'clients/client_create.html'
    model = Client
    success_url = reverse_lazy('client_list')
    fields = ['name',
              'web_site',
              'phone',
              'address',
              'is_active',
              'description']


class ClientEditView(UpdateView):
    template_name = 'clients/client_edit.html'
    model = Client
    success_url = reverse_lazy('client_list')
    fields = ['name',
              'web_site',
              'phone',
              'address',
              'is_active',
              'description']

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if not self.request.user.has_perm('clients.change_client'):
            raise PermissionDenied()
        return super().post(request, *args, **kwargs)


class ClientDeleteView(PermissionRequiredMixin, DeleteView):
    permission_required = 'clients.delete_client'
    model = Client
    success_url = reverse_lazy("client_list")


class ContactListView(ListView):
    model = Contact
    context_object_name = 'contacts'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['client'] = Client.objects.get(id=self.kwargs['fk'])
        return context

    def get_queryset(self):
        return Contact.objects \
                    .filter(client=self.kwargs['fk']) \
                    .order_by('contact')


class ContactCreateView(PermissionRequiredMixin, CreateView):
    permission_required = 'clients.add_contact'
    template_name = 'clients/contact_create.html'
    model = Contact
    fields = ['contact', 'fio', 'description']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['client'] = Client.objects.get(id=self.kwargs['fk'])
        return context

    def get_initial(self):
        data = {'client': self.kwargs['fk']}
        if self.kwargs.get('contact'):
            data['contact'] = self.kwargs['contact']
        return data

    def dispatch(self, request, *args, **kwargs):
        self.client = Client.objects.get(id=self.kwargs['fk'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.client = self.client
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("contact_list", kwargs={'fk': self.kwargs['fk']})


class ContactEditView(UpdateView):
    template_name = 'clients/contact_edit.html'
    model = Contact
    fields = ['contact', 'fio', 'description']

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if not self.request.user.has_perm('clients.change_contact'):
            raise PermissionDenied()
        return super().post(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy("contact_list", kwargs={'fk': self.kwargs['fk']})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['client'] = Client.objects.get(id=self.kwargs['fk'])
        return context


class ContactDeleteView(PermissionRequiredMixin, DeleteView):
    permission_required = 'clients.delete_contact'
    model = Contact

    def get_success_url(self):
        return reverse_lazy("contact_list", kwargs={'fk': self.kwargs['fk']})
