from collections import namedtuple

from django.forms import CharField, ModelForm, ValidationError, modelformset_factory
from django.forms.formsets import BaseFormSet

from .fields import PartColorChoiceField
from .models import Inventory, UserPart
from .widgets import CustomSelectWidget


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


class InventoryForm(ModelForm):
    rgb = CharField(disabled=True, required=False)

    class Meta:
        model = Inventory
        fields = ['color', 'rgb', 'qty']

    def __init__(self, *args, userpart, **kwargs):
        super().__init__(*args, **kwargs)
        self.initial_data = {}

        # Exclude existing colors from New Forms
        queryset = userpart.part.available_colors
        if 'initial' in kwargs:
            self.initial_data = kwargs['initial']
        else:
            queryset = userpart.unused_colors

        self.userpart = userpart
        self.fields['color'] = PartColorChoiceField(
            label='Available Colors',
            required=True,
            queryset=queryset,
            widget=CustomSelectWidget(attrs={'class': 'chosen-select'}))

    @property
    def initial_color(self):
        return self.initial_data['color'] if 'color' in self.initial_data else None

    @property
    def submitted_color(self):
        return self.cleaned_data['color'] if 'color' in self.cleaned_data else None

    @property
    def color_changed(self):
        return self.initial_color != self.submitted_color

    @property
    def initial_qty(self):
        return self.initial_data['qty'] if 'qty' in self.initial_data else None

    @property
    def submitted_qty(self):
        return self.cleaned_data['qty'] if 'qty' in self.cleaned_data else None

    @property
    def qty_changed(self):
        return self.initial_qty != self.submitted_qty

    @property
    def marked_for_deletion(self):
        return ('DELETE' in self.cleaned_data) and self.cleaned_data['DELETE']

    @property
    def initial_values_cleared(self):
        return self.initial_color and not self.submitted_color and (self.submitted_qty is None)

    def is_valid(self):
        valid = super().is_valid()  # This will set cleaned_data

        if (self.submitted_color or (self.submitted_qty is not None)) and not self.marked_for_deletion:
            return valid

        return True

    def get_form_actions(self):
        FormActions = namedtuple('FormActions', 'create update delete')

        create_color = ()
        update_color = ()
        delete_color = None

        if self.is_valid():
            # Delete if marked, cleared or replace
            if (self.marked_for_deletion or self.initial_values_cleared or
                    (self.initial_color and self.color_changed)):
                if self.initial_color:
                    delete_color = self.initial_color

            # Create if not marked for deletion and have a new color
            if not self.marked_for_deletion:
                if self.submitted_color:
                    if self.color_changed:
                        create_color = (self.submitted_color, self.submitted_qty)
                    elif self.qty_changed:
                        update_color = (self.submitted_color, self.submitted_qty)

        return FormActions(create_color, update_color, delete_color)

    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.save()
        return instance


class BaseInventoryFormset(BaseFormSet):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        userpart = kwargs.get('form_kwargs').get('userpart')

        self.queryset = Inventory.objects.filter(userpart=userpart)

    # See https://whoisnicoleharris.com/2015/01/06/implementing-django-formsets.html
    def clean(self):
        """
        Adds Validation that no 2 forms have the same color.
        """

        color_list = []
        duplicates = []

        # Don't need to validate if invalid forms are found
        if any(self.errors):
            return

        for form in self.forms:
            # Ignore Forms that are meant for deletion
            if self.can_delete and self._should_delete_form(form):  # pylint: disable=no-member
                continue

            color = form.cleaned_data.get('color')
            if color:
                if color.name in color_list:
                    duplicates.append(color.name)
                else:
                    color_list.append(color.name)

        if duplicates:
            raise ValidationError(F'Diplicate Colors Found: {set(duplicates)}',
                                  code='duplicate_colors')


InventoryFormset = modelformset_factory(
    Inventory, form=InventoryForm, formset=BaseInventoryFormset, extra=2,
    can_delete=True
)
