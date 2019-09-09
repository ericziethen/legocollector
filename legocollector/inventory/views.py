import csv
import io

from django.db import transaction
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms import ModelForm, ValidationError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import reverse
from django.urls import reverse_lazy
from django.views.generic import DeleteView, DetailView, ListView, UpdateView
from django.views.generic.edit import CreateView

from .models import Color, Part, UserPart, Inventory


@login_required
def import_userparts(request):
    # Implementation example at https://www.pythoncircle.com/post/30/how-to-upload-and-process-the-csv-file-in-django/

    csv_file = request.FILES['csv_file']
    if not csv_file.name.lower().endswith('.csv'):
        messages.error(request, 'File does not have a csv extension')
        return HttpResponseRedirect(reverse('home'))

    # if file is too large, return
    if csv_file.multiple_chunks():
        messages.error(request, 'Uploaded file is too big (%.2f MB).' % (csv_file.size / (1000 * 1000),))
        return HttpResponseRedirect(reverse('home'))

    csv_file.seek(0)
    reader = csv.DictReader(io.StringIO(csv_file.read().decode('utf-8')))
    with transaction.atomic():
        for row in reader:
            userpart, _ = UserPart.objects.get_or_create(
                user=request.user,
                part=Part.objects.get(part_num=row['Part']),
                color=Color.objects.get(id=row['Color']),
            )

            userpart.qty = row['Quantity']
            userpart.save()

    messages.info(request, F'"{csv_file}" processed ok')
    return HttpResponseRedirect(reverse('home'))


@login_required
def export_userparts(request):
    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="userpartlist.csv"'

    userparts = UserPart.objects.filter(user=request.user)
    writer = csv.writer(response)
    writer.writerow(['Part', 'Color', 'Quantity'])
    for userpart in userparts:
        writer.writerow([userpart.part.part_num, userpart.color.id, userpart.qty])
    return response


class UserPartCreateForm(ModelForm):
    class Meta:
        model = UserPart
        fields = ('part', 'color', 'qty')

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super().__init__(*args, **kwargs)

    def clean(self):
        # Get the cleaned data
        cleaned_data = super().clean()

        # Find the unique_together fields
        part = cleaned_data.get('part')
        color = cleaned_data.get('color')

        if UserPart.objects.filter(user=self.user, part=part, color=color).exists():
            raise ValidationError('You already have this Userpart in your list.')

        return cleaned_data


class UserPartUpdateForm(ModelForm):
    class Meta:
        model = UserPart
        fields = ('color', 'qty')

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        self.color = kwargs.pop('color')
        self.part = kwargs.pop('part')
        super().__init__(*args, **kwargs)

    def clean(self):
        # Get the cleaned data
        cleaned_data = super().clean()

        # Find the unique_together fields
        form_color = cleaned_data.get('color')

        if form_color != self.color:
            if UserPart.objects.filter(user=self.user, part=self.part, color=form_color).exists():
                raise ValidationError('You already have this Userpart in your list.')

        return cleaned_data


class UserPartCreateView(LoginRequiredMixin, CreateView):  # pylint: disable=too-many-ancestors
    model = UserPart
    template_name = 'inventory/userpart_create.html'
    form_class = UserPartCreateForm

    def form_valid(self, form):
        form.instance.user = self.request.user
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
        form.instance.user = self.request.user
        try:
            return super().form_valid(form)
        except ValidationError:
            form.add_error(None, 'You already have a Part with this color in your list')
            return super().form_invalid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({'user': self.request.user, 'part': self.object.part, 'color': self.object.color})
        return kwargs


class UserPartDeleteView(LoginRequiredMixin, DeleteView):  # pylint: disable=too-many-ancestors
    model = UserPart
    template_name = 'inventory/userpart_delete.html'
    success_url = reverse_lazy('home')


class UserPartDetailView(LoginRequiredMixin, DetailView):  # pylint: disable=too-many-ancestors
    model = UserPart
    template_name = 'inventory/userpart_detail.html'


    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        context['inventory_list'] = Inventory.objects.filter(userpart=self.object.id)
        return context






class UserPartListView(LoginRequiredMixin, ListView):  # pylint: disable=too-many-ancestors
    model = UserPart

    def get_queryset(self):
        """Only for current user."""
        return UserPart.objects.filter(user=self.request.user)



'''
Here's what I wanted in a Class Based View (CBV), my explanation of my issue was not very clear.

def get_context_data(self, **kwargs):
get_context_data is a way to get data that is not normally apart of a generic view. Vehicle is already provided to the View because its the model defined for it, if you wanted to pass objects from a different model you would need to provide a new context, get_context_data is the way to do this. statusUpdate is a model with a foreign key to Vehicle. Full example below.

class VehicleDetail(generic.DetailView):
    model = Vehicle
    template_name = 'fleetdb/detail.html'


    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(VehicleDetail, self).get_context_data(**kwargs)
        context['updates'] = statusUpdate.objects.filter(vehicle_id=1).order_by('-dateTime')[:5]
        return context
'''


