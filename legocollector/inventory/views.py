import csv
import io

from django.db import transaction
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms import ModelForm, ValidationError, modelformset_factory
from django.forms.formsets import BaseFormSet

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import reverse
from django.urls import reverse_lazy
from django.views.generic import DeleteView, DetailView, ListView, UpdateView
from django.views.generic.edit import CreateView

import django_filters as filters
from django_filters.views import FilterView

from django_tables2.views import SingleTableMixin

from .models import Color, Part, UserPart, Inventory
from .tables import PartTable, UserPartTable

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
        # print('UserPartDetailView.get_context_data() - ENTER')
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        context['inventory_list'] = Inventory.objects.filter(userpart=self.object.id)
        # print('UserPartDetailView.get_context_data() - EXIT')
        return context



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
            raise ValidationError(F'You already have {color} in your list.')

        return cleaned_data


class PartFilter(filters.FilterSet):
    part_num_contains = filters.CharFilter(field_name='part_num', lookup_expr='icontains')

    class Meta:
        model = Part
        fields = ('part_num', 'name', 'width', 'height', 'length', 'stud_count', 'multi_height',
                  'uneven_dimensions', 'category_id')





class FilteredPartListUserPartCreateView(LoginRequiredMixin, SingleTableMixin, FilterView):   # pylint: disable=too-many-ancestors
    model = Part
    template_name = 'inventory/userpart_from_part_create.html'
    table_class = PartTable
    filterset_class = PartFilter

    def post(self, request, **kwargs):
        try:
            part_id = self.get_part_id_from_post()
        except ValidationError as error:
            messages.error(self.request, str(error))
            return HttpResponseRedirect(reverse_lazy('userpart_create'))
        else:
            userpart = UserPart.objects.create(
                user=self.request.user,
                part_id=part_id)
            userpart.save()
            return HttpResponseRedirect(reverse_lazy('userpart_detail', kwargs={'pk1': userpart.pk}))

    # Don't use form_valid as name since we are not inheriting a Form
    # Not the best name but ok for now
    def get_part_id_from_post(self):
        # Get all Selected Checkboxes
        ids = self.request.POST.getlist('box_selection')

        # Ensure exactly 1 Checkbox has been selected
        ids_count = len(ids)
        if ids_count != 1:
            raise ValidationError(F'Select exactly 1 part to add, you selected {ids_count}')

        part_id = ids[0]
        # Ensure we don't already have this part
        if UserPart.objects.filter(user=self.request.user, part=part_id).exists():
            raise ValidationError(F'You already have this part in your list')

        # Return the Primary Key
        return part_id


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
        return self.get_success_url()

    def get_success_url(self):
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


class InventoryForm(ModelForm):
    class Meta:
        model = Inventory
        fields = ['color', 'qty']

    def __init__(self, *args, userpart, **kwargs):

        # print('InventoryForm.__init__()')
        self.userpart = userpart
        # print(F'  Userpart init: {userpart}')
        # print(F'  Userpart: {self.userpart}')
        # print(F'  Type Userpart: {type(self.userpart)}')
        # kwargs.update({'userpart': self.kwargs.get('pk1', '')})
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        # print('InventoryForm.save() - ENTER')
        instance = super().save(commit=False)
        if commit:
            # print('InventoryForm.save() - commit')
            instance.save()
        # print('InventoryForm.save() - EXIT')
        return instance


class BaseInventoryFormset(BaseFormSet):

    def __init__(self, *args, **kwargs):
        # print('BaseInventoryFormset.__init__() - ENTER')
        super().__init__(*args, **kwargs)

        # print(F'kwargs::: {kwargs}')
        # create filtering here whatever that suits you needs
        # print('userpart', kwargs.get('userpart'))
        # print('userpart2', kwargs.get('form_kwargs').get('userpart'))

        userpart = kwargs.get('form_kwargs').get('userpart')

        self.queryset = Inventory.objects.filter(userpart=userpart)
        # print('queryset', self.queryset)
        # print('BaseInventoryFormset.__init__() - EXIT')

    '''  # pylint: disable=pointless-string-statement
    NOT WORKING YET - Probably need to check for duplicate colors
    # See https://whoisnicoleharris.com/2015/01/06/implementing-django-formsets.html
    def clean(self):
        """
        Adds Validation that no 2 forms have the same color.
        """
        print('BaseInventoryFormset.clean() - ENTER')

        color_list = []
        duplicates = False

        # Don't need to validata if invalid forms are found
        print(F'  Check Errors::: {self.errors}')
        if any(self.errors):
            print( '  -> Errors Found')
            return

        for form in self.forms:
            print(F' Check Form:')
            # Ignore Forms that are meant for deletion
            if self.can_delete and self._should_delete_form(form):
                print('  Ignoring form Meant for Deletion')
                continue

            color = form.cleaned_data.get('color')
            if color and color in color_list:
                duplicates = True
            color_list.append(color)
            print(F'  Color: "{color}" - List: {color_list}')

            # !!! NOT WORKING YET !!!
            if duplicates:
                print('Raise Validation Error')
                raise ValidationError(
                    'Inventories must have unique colors.',
                    code='duplicate_colors'
                )
        print('BaseInventoryFormset.clean() - EXIT')
    '''  # pylint: disable=pointless-string-statement


InventoryFormset = modelformset_factory(
    Inventory, form=InventoryForm, formset=BaseInventoryFormset, extra=2
)


class UserPartManageColorsView(LoginRequiredMixin, UpdateView):  # pylint: disable=too-many-ancestors
    model = UserPart
    fields = []
    template_name = 'inventory/userpart_manage_colors.html'
    pk_url_kwarg = 'pk1'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        initial_data = [{'color': inv.color, 'qty': inv.qty}
                        for inv in Inventory.objects.filter(userpart=self.object)]
        if self.request.POST:
            context['inventory_list'] = InventoryFormset(self.request.POST, initial=initial_data,
                                                         form_kwargs={'userpart': self.object})
        else:
            context['inventory_list'] = InventoryFormset(initial=initial_data, form_kwargs={'userpart': self.object})
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        inventory_formset = context['inventory_list']

        # Verify the Forms and Formset - Maybe needed??? Maybe not
        # inventory_formset.full_clean()

        for inventory_form in inventory_formset:
            if inventory_form.is_valid():
                # Check that it's not a blank unchanged form
                if (('color' in inventory_form.cleaned_data) and ('qty' in inventory_form.cleaned_data)):
                    color = inventory_form.cleaned_data['color']
                    qty = inventory_form.cleaned_data['qty']

                    inventory, _ = Inventory.objects.get_or_create(userpart=self.object,
                                                                   color=color)
                    inventory.qty = qty
                    inventory.save()
            else:
                form.add_error(None, 'Invalid Form')
                return super().form_invalid(form)

        return super().form_valid(form)
