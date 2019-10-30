from django.contrib.auth.models import User
from django.test import TestCase

from inventory.forms import InventoryForm
from inventory.models import Part, PartCategory, UserPart


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

    def run_form_test(self, expected_value, *, color=None, qty=None, removed=None, initial=None):
        form_data = {}
        if color:
            form_data['color'] = 'Black'
        if qty:
            form_data['qty'] = '15'
        if removed:
            form_data['DELETE'] = True
        if initial:
            form_data['initial_data'] = {'color': 'Red'}

        form = InventoryForm(userpart=self.user_part, data=form_data)
        form.full_clean()
        if expected_value:
            self.assertTrue(form.is_valid(), str(form.errors) + F'\n\nCleaned Data: {form.cleaned_data}')
        else:
            self.assertFalse(form.is_valid(), str(form.errors) + F'\n\nCleaned Data: {form.cleaned_data}')

    def test_empty_form(self):
        self.run_form_test(True)

    def test_removed_empty_form(self):
        self.run_form_test(True, removed=True)

    def test_form_only_qty(self):
        self.run_form_test(False, qty=True)

    def test_form_only_initial_data(self):
        self.run_form_test(True, initial=True)

    '''
    def test_form_only_color(self):
        self.run_form_test({'color': '15'}, False)
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