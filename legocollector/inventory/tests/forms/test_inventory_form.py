from django.contrib.auth.models import User
from django.test import TestCase

from inventory.forms import InventoryForm
from inventory.models import Color, Part, PartCategory, SetPart, UserPart


class TestFormValidity(TestCase):

    def setUp(self):
        self.initian_data = {'initial_data': True}
        self.no_initian_data = {}

        self.user = User.objects.create_user(  # nosec
            username='User', email='jacob@…', password='top_secret')

        self.part_category = PartCategory.objects.create(id=1, name='category')

        self.part = Part.objects.create(
            part_num='Part', name='A Part', category=self.part_category)

        self.user_part = UserPart.objects.create(user=self.user, part=self.part)

        self.color_red = Color.objects.create(id='4', name='Red', rgb='C91A09')

        self.set_part1 = SetPart.objects.create(
            set_inventory=1, part=self.part, color=self.color_red, qty=1, is_spare=False)

    def run_form(self, *, color=None, qty=None, removed=None, initial=None):
        form_data = {}
        if color:
            form_data['color'] = self.color_red.pk
        if qty:
            form_data['qty'] = '15'

        form = InventoryForm(userpart=self.user_part, data=form_data)
        form.full_clean()
        
        if initial:
            form.initial_data = {'color': self.color_red, 'qty': 0}
        if removed:
            form.cleaned_data['DELETE'] = True

        return form

    def run_form_is_valid_test(self, expected_value, *, color=None, qty=None, removed=None, initial=None):
        form = self.run_form(color=color, qty=qty, removed=removed, initial=initial)
        if expected_value:
            self.assertTrue(form.is_valid(), str(form.errors) + F'\n\nCleaned Data: {form.cleaned_data}')
        else:
            self.assertFalse(form.is_valid(), str(form.errors) + F'\n\nCleaned Data: {form.cleaned_data}')

    def test_cleaned_data_populated(self):
        form = self.run_form(color=True, qty=True, removed=True, initial=True)

        self.assertIn('color', form.cleaned_data)
        self.assertIn('qty', form.cleaned_data)
        self.assertTrue(form.initial_data)
        self.assertIn('DELETE', form.cleaned_data)

    def test_empty_form(self):
        self.run_form_is_valid_test(True)

    def test_removed_empty_form(self):
        self.run_form_is_valid_test(True, removed=True)

    def test_form_only_qty(self):
        self.run_form_is_valid_test(False, qty=True)

    def test_form_only_initial_data(self):
        self.run_form_is_valid_test(True, initial=True)

    def test_form_only_color(self):
        self.run_form_is_valid_test(False, color=True)

    def test_form_color_qty(self):
        self.run_form_is_valid_test(True, color=True, qty=True)

    def test_form_initial_qty(self):
        self.run_form_is_valid_test(False, initial=True, qty=True)

    '''
    def test_form_removed_qty(self):
        self.run_form_is_valid_test(True, removed=True, qty=True)
    '''

'''
'color', 'qty', 'DELETE', 'initial_data'


class MyTests(TestCase):
    def test_forms(self):
        form_data = {'something': 'something'}
        form = MyForm(data=form_data)
        self.assertTrue(form.is_valid())
ng self.assertTrue(form.isVald(), form.errors)
'''