from django.forms import ModelForm, ValidationError, modelformset_factory
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
