from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms import ModelForm, ValidationError
from django.urls import reverse_lazy
from django.views.generic import DeleteView, DetailView, ListView, UpdateView
from django.views.generic.edit import CreateView

from .models import UserPart


class UserPartCreateForm(ModelForm):
    class Meta:
        model = UserPart
        fields = ('part_num', 'color', 'qty')

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super().__init__(*args, **kwargs)

    def clean(self):
        # Get the cleaned data
        cleaned_data = super().clean()

        # Find the unique_together fields
        part_num = cleaned_data.get('part_num')
        color = cleaned_data.get('color')

        if UserPart.objects.filter(user_id=self.user, part_num=part_num, color=color).exists():
            raise ValidationError('You already have this Userpart in your list.')

        return cleaned_data


class UserPartUpdateForm(ModelForm):
    class Meta:
        model = UserPart
        fields = ('color', 'qty')

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')        
        self.part_num = kwargs.pop('part_num')
        super().__init__(*args, **kwargs)

    def clean(self):
        # Get the cleaned data
        cleaned_data = super().clean()

        # Find the unique_together fields
        color = cleaned_data.get('color')

        if UserPart.objects.filter(user_id=self.user, part_num=self.part_num, color=color).exists():
            raise ValidationError('You already have this Userpart in your list.')

        return cleaned_data


class UserPartCreateView(LoginRequiredMixin, CreateView):  # pylint: disable=too-many-ancestors
    model = UserPart
    template_name = 'inventory/userpart_create.html'
    form_class = UserPartCreateForm

    def form_valid(self, form):
        form.instance.user_id = self.request.user
        try:
            return super().form_valid(form)
        except ValidationError:
            form.add_error(None, 'You already have a Part with this color in your list')
            return super().form_invalid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return kwargs


class UserPartUpdateView(LoginRequiredMixin, UpdateView):  # pylint: disable=too-many-ancestors
    model = UserPart
    template_name = 'inventory/userpart_update.html'
    form_class = UserPartUpdateForm

    def form_valid(self, form):
        form.instance.user_id = self.request.user
        try:
            return super().form_valid(form)
        except ValidationError:
            form.add_error(None, 'You already have a Part with this color in your list')
            return super().form_invalid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({'user': self.request.user, 'part_num': self.object.part_num})
        return kwargs


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
