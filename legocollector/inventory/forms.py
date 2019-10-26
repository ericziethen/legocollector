from django.forms import CharField, ModelForm, ValidationError, modelformset_factory
from django.forms.formsets import BaseFormSet

from .models import Inventory, UserPart


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





from django.forms import ModelChoiceField, Select
from .models import Color
# https://stackoverflow.com/questions/5089396/django-form-field-choices-adding-an-attribute
class CustomSelect(Select):
    def __init__(self, attrs=None, choices=()):
        self.custom_attrs = {}
        super().__init__(attrs, choices)

    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        index = str(index) if subindex is None else "%s_%s" % (index, subindex)
        if attrs is None:
            attrs = {}
        option_attrs = self.build_attrs(self.attrs, attrs) if self.option_inherits_attrs else {}
        if selected:
            option_attrs.update(self.checked_attribute)
        if 'id' in option_attrs:
            option_attrs['id'] = self.id_for_label(option_attrs['id'], index)

        # setting the attributes here for the option
        if len(self.custom_attrs) > 0:
            if value in self.custom_attrs:
                custom_attr = self.custom_attrs[value]
                for k, v in custom_attr.items():
                    option_attrs.update({k: v})

        return {
            'name': name,
            'value': value,
            'label': label,
            'selected': selected,
            'index': index,
            'attrs': option_attrs,
            'type': self.input_type,
            'template_name': self.option_template_name,
        }


class MyModelChoiceField(ModelChoiceField):

    # custom method to label the option field
    def label_from_instance(self, obj):
        # since the object is accessible here you can set the extra attributes
        if hasattr(obj, 'rgb'):
            self.widget.custom_attrs.update({obj.pk: {'rgb': obj.rgb}})
            self.widget.custom_attrs.update({obj.pk: {'style': F'background-color:#{obj.rgb}'}})
        #return obj.get_display_name()
        #return obj.name + F' style="background-color:#{obj.rgb}"'
        return obj.name

class InventoryForm(ModelForm):
    rgb = CharField(disabled=True, required=False)

    field1 = MyModelChoiceField(required=True,
                                queryset=Color.objects.all().order_by('name'),
                                widget=CustomSelect(attrs={'class': 'chosen-select'}))

    class Meta:
        model = Inventory
        fields = ['color', 'rgb', 'qty', 'field1']

    def __init__(self, *args, userpart, **kwargs):
        super().__init__(*args, **kwargs)
        self.userpart = userpart

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
