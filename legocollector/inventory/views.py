import csv
import io

from django.db import transaction
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import reverse
from django.urls import reverse_lazy
from django.views.generic import DeleteView, DetailView, ListView, UpdateView
from django.views.generic.edit import CreateView

from .filters import (
    UserPartFilter, PartFilter,
    FilterView
)
from .forms import (
    UserPartUpdateForm,
    InventoryCreateForm, InventoryUpdateForm,
    InventoryFormset,
    ValidationError
)
from .models import Color, Part, UserPart, Inventory
from .tables import (
    PartTable, UserPartTable,
    SingleTableMixin
)

from common.util import url_helper


def convert_color_id_to_rgb(request):
    color_id = request.GET.get('color_id', None)

    rgb = ''
    complimentary_color = ''
    if color_id:
        color = Color.objects.filter(id=color_id).first()
        if color:
            rgb = color.rgb
            complimentary_color = color.complimentary_color
    data = {
        'rbg_val': rgb,
        'complimentary_color': complimentary_color
    }
    return JsonResponse(data)


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
            userpart, _ = UserPart.objects.update_or_create(
                user=request.user,
                part=Part.objects.get(part_num=row['Part']),
            )
            inventory, _ = Inventory.objects.update_or_create(
                userpart=userpart,
                color=Color.objects.get(id=row['Color']),
                defaults={'qty': row['Quantity']}
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


class ColorListView(ListView):  # pylint: disable=too-many-ancestors
    model = Color
    template_name = 'inventory/color_list.html'

    def get_queryset(self):
        return Color.objects.all()


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


class UserPartListView(LoginRequiredMixin, SingleTableMixin, FilterView):  # pylint: disable=too-many-ancestors
    model = UserPart
    template_name = 'inventory/userpart_list.html'
    table_class = UserPartTable
    filterset_class = UserPartFilter

    def get_queryset(self):
        """Only for current user."""
        return UserPart.objects.filter(user=self.request.user)


class FilteredPartListUserPartCreateView(LoginRequiredMixin, SingleTableMixin, FilterView):   # pylint: disable=too-many-ancestors
    model = Part
    template_name = 'inventory/userpart_from_part_create.html'
    table_class = PartTable
    filterset_class = PartFilter

    def post(self, request, **kwargs):
        try:
            part_id_list = self.get_part_ids_from_post()
        except ValidationError as error:
            messages.error(self.request, str(error))
            # Inspired by https://stackoverflow.com/questions/9585491/how-do-i-pass-get-parameters-using-django-urlresolvers-reverse
            response = HttpResponseRedirect(reverse_lazy('userpart_create'))
            get_params_dic = {param: request.GET.get(param) for param in request.GET.keys() if request.GET.get(param)}
            url = url_helper.build_url(response.url, get_params_dic)
            response['Location'] = url
            return response
        else:
            for part_id in part_id_list:
                userpart = UserPart.objects.create(
                    user=self.request.user,
                    part_id=part_id)
                userpart.save()

                if len(part_id_list) == 1:
                    return HttpResponseRedirect(reverse_lazy('userpart_detail', kwargs={'pk1': userpart.pk}))

            return HttpResponseRedirect(reverse_lazy('userpart_list'))

    # Don't use form_valid as name since we are not inheriting a Form
    # Not the best name but ok for now
    def get_part_ids_from_post(self):
        # Get all Selected Checkboxes
        ids = self.request.POST.getlist('box_selection')

        # Ensure at least 1 Checkbox has been selected
        if not ids:
            raise ValidationError(F'Select at least 1 part to add, you selected none')

        part_id_list = []
        for part_id in ids:
            # Ensure we don't already have this part
            if UserPart.objects.filter(user=self.request.user, part=part_id).exists():
                raise ValidationError(F'You already have this part in your list')
            part_id_list.append(part_id)

        # Return the Primary Key
        return part_id_list

    def get_queryset(self):
        """Only parts we don't have already."""
        return Part.objects.filter(~Q(user_parts__user=self.request.user))


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

        # Check for Form Errors
        for inventory_form in inventory_formset:
            if not inventory_form.is_valid():
                form.add_error(None, 'Invalid Form')
                return super().form_invalid(form)

        # Check for Non-Form errors
        if inventory_formset.non_form_errors():
            return super().form_invalid(form)

        create_or_update_dic = {}
        delete_dic = {}
        # Collect all form actions
        for inventory_form in inventory_formset:
            form_actions = inventory_form.get_form_actions()

            if form_actions.create:
                create_or_update_dic[form_actions.create[0].pk] = form_actions.create
            if form_actions.update:
                create_or_update_dic[form_actions.update[0].pk] = form_actions.update
            if form_actions.delete:
                delete_dic[form_actions.delete.pk] = form_actions.delete

        # Delete all items that need deleting
        for color_pk, color in delete_dic.items():
            # If the Item is in the the Update or Create list we don't need to actually delete it first
            if color_pk not in create_or_update_dic:
                Inventory.objects.filter(userpart=self.object, color=color).delete()

        # Create/Update Items
        for _, inventory_tuple in create_or_update_dic.items():
            Inventory.objects.update_or_create(
                userpart=self.object,
                color=inventory_tuple[0],
                defaults={'qty': inventory_tuple[1]}
            )

        return super().form_valid(form)
