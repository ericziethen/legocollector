from django.contrib.auth.models import User
from django.test import TestCase

from inventory.forms import InventoryForm
from inventory.models import Color, Part, PartCategory, SetPart, UserPart


class TestFormProcessing(TestCase):

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
        self.color_black = Color.objects.create(id='20', name='Black', rgb='000000')

        self.set_part1 = SetPart.objects.create(
            set_inventory=1, part=self.part, color=self.color_red, qty=1, is_spare=False)
        self.set_part2 = SetPart.objects.create(
            set_inventory=2, part=self.part, color=self.color_black, qty=1, is_spare=False)

    def run_form(self, *, new_color=None, new_qty=None, removed=None,
                 initial_color=None, initial_qty=20):

        form_data = {}
        if new_color:
            form_data['color'] = new_color.pk
        if new_qty:
            form_data['qty'] = new_qty

        form = InventoryForm(userpart=self.user_part, data=form_data)

        if initial_color:
            self.assertIsNotNone(initial_qty)
            form.initial_data = {'color': initial_color, 'qty': initial_qty}

        form.full_clean()

        if removed:
            form.cleaned_data['DELETE'] = True

        return form

    #########################################
    ###### Start of Form Validity Tests #####
    #########################################
    def run_form_is_valid_test(self, expected_value, *, new_color=None, new_qty=None, removed=None, initial_color=None):
        form = self.run_form(new_color=new_color, new_qty=new_qty, removed=removed, initial_color=initial_color)
        
        #print(F'\nCleaned Data: {form.cleaned_data}')
        #print(F'  Initial Data: {form.initial_data}')
        #print(F'  Changed Data: {form.changed_data}')
        if expected_value:
            self.assertTrue(form.is_valid(), str(form.errors) + F'\n\nCleaned Data: {form.cleaned_data}')
        else:
            self.assertFalse(form.is_valid(), str(form.errors) + F'\n\nCleaned Data: {form.cleaned_data}')

    def test_cleaned_data_populated(self):
        form = self.run_form(new_color=self.color_red, new_qty=10, removed=True, initial_color=self.color_black)

        self.assertIn('color', form.cleaned_data)
        self.assertIn('qty', form.cleaned_data)
        self.assertTrue(form.initial_data)
        self.assertIn('DELETE', form.cleaned_data)

    def test_empty_form(self):
        self.run_form_is_valid_test(True)

    def test_remove_form_always_valid(self):
        self.run_form_is_valid_test(True, removed=True)
        self.run_form_is_valid_test(True, removed=True, new_color=self.color_red)
        self.run_form_is_valid_test(True, removed=True, new_color=self.color_red, new_qty=10)
        self.run_form_is_valid_test(True, removed=True, initial_color=self.color_black)
        self.run_form_is_valid_test(True, removed=True, initial_color=self.color_black, new_color=self.color_red)
        self.run_form_is_valid_test(True, removed=True, initial_color=self.color_black, new_color=self.color_red, new_qty=10)
        self.run_form_is_valid_test(True, removed=True, initial_color=self.color_black, new_qty=10)
        self.run_form_is_valid_test(True, removed=True, new_qty=10)

    def test_form_values_removed_for_deletion(self):
        self.run_form_is_valid_test(True, initial_color=self.color_black)

    def test_form_newly_populated_form(self):
        self.run_form_is_valid_test(True, new_color=self.color_red, new_qty=10)

    def test_form_unchanged(self):
        self.run_form_is_valid_test(True, initial_color=self.color_black, new_color=self.color_red, new_qty=10)

    def test_form_new_form_incomplete(self):
        self.run_form_is_valid_test(False, new_qty=10)
        self.run_form_is_valid_test(False, new_color=self.color_red)

    def test_form_incomplete_after_edit(self):
        self.run_form_is_valid_test(False, initial_color=self.color_black, new_qty=10)
        self.run_form_is_valid_test(False, initial_color=self.color_black, new_color=self.color_red)

    #######################################
    ###### Start of Form Action Tests #####
    #######################################
    def run_form_action_test(self, *, expected_create, expected_update, expected_delete,
                             new_color=None, new_qty=None, removed=None, initial_color=None, initial_qty=None):
        form = self.run_form(new_color=new_color, new_qty=new_qty, removed=removed, initial_color=initial_color, initial_qty=initial_qty)

        form_action = form.get_form_actions()

        if expected_create:
            self.assertTupleEqual(form_action.create, expected_create)

        if expected_update:
            self.assertTupleEqual(form_action.update, expected_update)

        if expected_delete:
            self.assertEqual(form_action.delete, expected_delete)

    def test_new_form_blank(self):
        self.run_form_action_test(expected_create=(), expected_update=(), expected_delete=None)
