from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import DeleteView, DetailView, ListView, UpdateView
from django.views.generic.edit import CreateView

from .models import UserPart


class UserPartCreateView(LoginRequiredMixin, CreateView):  # pylint: disable=too-many-ancestors
    model = UserPart
    template_name = 'inventory/userpart_create.html'
    fields = ['part_num', 'color']

    def form_valid(self, form):
        form.instance.user_id = self.request.user
        return super().form_valid(form)


class UserPartUpdateView(LoginRequiredMixin, UpdateView):  # pylint: disable=too-many-ancestors
    model = UserPart
    template_name = 'inventory/userpart_update.html'
    fields = ['part_num', 'color']


class UserPartDeleteView(LoginRequiredMixin, DeleteView):  # pylint: disable=too-many-ancestors
    model = UserPart
    template_name = 'inventory/userpart_delete.html'
    success_url = reverse_lazy('home')


class UserPartDetailView(LoginRequiredMixin, DetailView):  # pylint: disable=too-many-ancestors
    model = UserPart
    template_name = 'inventory/userpart_detail.html'


class UserPartListView(LoginRequiredMixin, ListView):  # pylint: disable=too-many-ancestors
    model = UserPart

    def get_queryset(self):
        """Only for current user."""
        return UserPart.objects.filter(user_id=self.request.user)
