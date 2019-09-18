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
from django.views.generic import DeleteView, DetailView, FormView, ListView, UpdateView
from django.views.generic.edit import CreateView

import django_filters as filters

import django_tables2 as tables
from django_tables2 import LinkColumn, Table
from django_tables2.utils import Accessor
from django_tables2.views import SingleTableMixin

from .models import Color, Part, UserPart, Inventory


@login_required
def import_userparts(request):
    # Implementation example at https://www.pythoncircle.com/post/30/how-to-upload-and-process-the-csv-file-in-django/

    csv_file = request.FILES['csv_file']
    if not csv_file.name.lower().endswith('.csv'):
        messages.error(request, 'File does not have a csv extension')
        return HttpResponseRedirect(reverse('userpart_list'))

    # if file is too large, return
    if csv_file.multiple_chunks():
        messages.error(request, 'Uploaded file is too big (%.2f MB).' % (csv_file.size / (1000 * 1000),))
        return HttpResponseRedirect(reverse('userpart_list'))

    csv_file.seek(0)
    reader = csv.DictReader(io.StringIO(csv_file.read().decode('utf-8')))
    with transaction.atomic():
        for row in reader:
            userpart, _ = UserPart.objects.get_or_create(
                user=request.user,
                part=Part.objects.get(part_num=row['Part']),
            )
            inventory, _ = Inventory.objects.get_or_create(
                userpart=userpart,
                color=Color.objects.get(id=row['Color']),
                qty=row['Quantity'],
            )

            inventory.save()
            userpart.save()

    messages.info(request, F'"{csv_file}" processed ok')
    return HttpResponseRedirect(reverse('userpart_list'))


@login_required
def export_userparts(request):
    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="userpartlist.csv"'

    userparts = UserPart.objects.filter(user=request.user)
    writer = csv.writer(response)
    writer.writerow(['Part', 'Color', 'Quantity'])
    for userpart in userparts:
        inventory_list = Inventory.objects.filter(userpart=userpart.id)
        for inv in inventory_list:
            writer.writerow([userpart.part.part_num, inv.color.id, inv.qty])
    return response


class UserPartCreateForm(ModelForm):
    class Meta:
        model = UserPart
        fields = ('part',)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super().__init__(*args, **kwargs)

    def clean(self):
        # Get the cleaned data
        cleaned_data = super().clean()

        # Find the unique_together fields
        part = cleaned_data.get('part')

        if UserPart.objects.filter(user=self.user, part=part).exists():
            raise ValidationError('You already have this Part in your list.')

        return cleaned_data


class UserPartUpdateForm(ModelForm):
    class Meta:
        model = UserPart
        fields = ('part',)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        self.part = kwargs.pop('part')
        super().__init__(*args, **kwargs)

    def clean(self):
        # Get the cleaned data
        cleaned_data = super().clean()

        # Find the unique_together fields
        form_part = cleaned_data.get('part')

        if form_part != self.part:
            if UserPart.objects.filter(user=self.user, part=form_part).exists():
                raise ValidationError('You already have this part in your list.')

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
            form.add_error(None, 'You already have this Part in your list')
            return super().form_invalid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return kwargs


class UserPartUpdateView(LoginRequiredMixin, UpdateView):  # pylint: disable=too-many-ancestors
    model = UserPart
    pk_url_kwarg = 'pk1'
    template_name = 'inventory/userpart_update.html'
    form_class = UserPartUpdateForm

    def form_valid(self, form):
        form.instance.user = self.request.user
        try:
            return super().form_valid(form)
        except ValidationError:
            form.add_error(None, 'You already have a Part in your list')
            return super().form_invalid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({'user': self.request.user, 'part': self.object.part})
        return kwargs


class UserPartDeleteView(LoginRequiredMixin, DeleteView):  # pylint: disable=too-many-ancestors
    model = UserPart
    pk_url_kwarg = 'pk1'
    template_name = 'inventory/userpart_delete.html'
    success_url = reverse_lazy('home')

    def get_cancel_url(self):
        userpart = self.kwargs['pk1']
        return reverse_lazy('userpart_detail', kwargs={'pk1': userpart})


class UserPartDetailView(LoginRequiredMixin, SingleTableMixin, DetailView):  # pylint: disable=too-many-ancestors
    model = UserPart
    pk_url_kwarg = 'pk1'
    template_name = 'inventory/userpart_detail.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        context['inventory_list'] = Inventory.objects.filter(userpart=self.object.id)
        return context


class UserPartTable(Table):
    part = LinkColumn(None, accessor='part.name', args=[Accessor('pk1')])

    class Meta:  # pylint: disable=too-few-public-methods
        model = UserPart
        fields = ['part', 'part.part_num', 'part.category_id', 'part.width', 'part.height', 'part.length',
                  'part.stud_count', 'part.multi_height', 'part.uneven_dimensions']


class UserPartListView(LoginRequiredMixin, SingleTableMixin, ListView):  # pylint: disable=too-many-ancestors
    model = UserPart
    table_class = UserPartTable

    def get_queryset(self):
        """Only for current user."""
        return UserPart.objects.filter(user=self.request.user)


class InventoryCreateForm(ModelForm):
    class Meta:
        model = Inventory
        fields = ('color', 'qty')

    def __init__(self, *args, **kwargs):
        self.userpart = kwargs.pop('userpart')
        super().__init__(*args, **kwargs)

    def clean(self):
        # Get the cleaned data
        cleaned_data = super().clean()

        # Find the unique_together fields
        color = cleaned_data.get('color')

        if Inventory.objects.filter(userpart=self.userpart, color=color).exists():
            raise ValidationError('You already have this Userpart in your list.')

        return cleaned_data







class PartFilter(filters.FilterSet):
    part_num_contains = filters.CharFilter(field_name='part_num', lookup_expr='icontains')

    class Meta:
        model = Part
        fields = ('part_num', 'name', 'width', 'height', 'length', 'stud_count', 'multi_height',
                  'uneven_dimensions', 'category_id')


class PartTable(Table):
    SELECT_BOX_TEMPLATE = """<input id="label" maxlength="16" name="label" type="text"/>"""
    label = tables.TemplateColumn(SELECT_BOX_TEMPLATE)
    box_selection = tables.CheckBoxColumn(accessor='pk')

    class Meta:
        model = Part
        fields = ('part_num', 'name', 'width', 'height', 'length', 'stud_count', 'multi_height',
                  'uneven_dimensions', 'category_id')
        attrs = {"class": "table-striped table-bordered"}
        empty_text = "No Parts Found"


class FilteredPartListUserPartCreateView(SingleTableMixin, FormView, filters.views.FilterView):
    model = Part
    template_name = 'inventory/userpart_from_part_create.html'
    table_class = PartTable
    filterset_class = PartFilter
    success_url = reverse('userpart_list')


    !!! COMPLETE ME BASED ON PLAYGROUND
    1.) Create Templates
    2.) Create Urls
    3.) Make Functions nice and secure !!!



























class InventoryCreateView(LoginRequiredMixin, CreateView):  # pylint: disable=too-many-ancestors
    model = Inventory
    template_name = 'inventory/inventory_create.html'
    form_class = InventoryCreateForm

    def form_valid(self, form):
        form.instance.userpart = UserPart.objects.get(id=self.kwargs.get('pk1', ''))
        try:
            return super().form_valid(form)
        except ValidationError:
            form.add_error(None, 'You already have a Part in this color in your list')
            return super().form_invalid(form)

    def get_cancel_url(self):
        userpart = self.kwargs['pk1']
        return reverse_lazy('userpart_detail', kwargs={'pk1': userpart})

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({'userpart': self.kwargs.get('pk1', '')})
        return kwargs


class InventoryUpdateForm(ModelForm):
    class Meta:
        model = Inventory
        fields = ('color', 'qty')

    def __init__(self, *args, **kwargs):
        self.userpart = kwargs.pop('userpart')
        self.color = kwargs.pop('color')
        super().__init__(*args, **kwargs)

    def clean(self):
        # Get the cleaned data
        cleaned_data = super().clean()

        # Find the unique_together fields
        form_color = cleaned_data.get('color')

        if form_color != self.color:
            if Inventory.objects.filter(userpart=self.userpart, color=form_color).exists():
                raise ValidationError('You already have this Inventory Color in your list.')

        return cleaned_data


class InventoryUpdateView(LoginRequiredMixin, UpdateView):  # pylint: disable=too-many-ancestors
    model = Inventory
    pk_url_kwarg = 'pk2'
    template_name = 'inventory/inventory_update.html'
    form_class = InventoryUpdateForm

    def form_valid(self, form):
        form.instance.userpart = UserPart.objects.get(id=self.kwargs.get('pk1', ''))
        try:
            return super().form_valid(form)
        except ValidationError:
            form.add_error(None, 'You already have a Part in this color in your list')
            return super().form_invalid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({'userpart': self.kwargs.get('pk1', ''), 'color': self.object.color})
        return kwargs


class InventoryDeleteView(LoginRequiredMixin, DeleteView):  # pylint: disable=too-many-ancestors
    model = Inventory
    pk_url_kwarg = 'pk2'
    template_name = 'inventory/inventory_delete.html'
    success_url = reverse_lazy('userpart_list')

    def get_cancel_url(self):
        userpart = self.kwargs['pk1']
        inventory = self.kwargs['pk2']
        return reverse_lazy('inventory_detail', kwargs={'pk1': userpart, 'pk2': inventory})


class InventoryDetailView(LoginRequiredMixin, DetailView):  # pylint: disable=too-many-ancestors
    model = Inventory
    pk_url_kwarg = 'pk2'
    template_name = 'inventory/inventory_detail.html'
