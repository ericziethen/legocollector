from django.contrib.auth.models import User
from django.test import TestCase

from inventory.models import Color, Inventory, Part, PartCategory, SetPart, UserPart


class TestInventoryColors(TestCase):  # pylint: disable=too-many-instance-attributes

    def setUp(self):
        print('run')
        self.user1 = User.objects.create_user(  # nosec
            username='User1', email='jacob@…', password='top_secret')
        self.user2 = User.objects.create_user(  # nosec
            username='User2', email='jacob2@…', password='top_secret')

        self.part_category1 = PartCategory.objects.create(id=1, name='category1')

        self.color1 = Color.objects.create(id='1', name='Red', rgb='AAAAAA')
        self.color2 = Color.objects.create(id='2', name='Blue', rgb='BBBBBB')
        self.color3 = Color.objects.create(id='3', name='Green', rgb='CCCCCC')

        self.part1 = Part.objects.create(
            part_num='PartA', name='A Part', category=self.part_category1)

        self.user_part1 = UserPart.objects.create(user=self.user1, part=self.part1)
        self.user_part2 = UserPart.objects.create(user=self.user2, part=self.part1)

        self.set_part1 = SetPart.objects.create(
            set_inventory=1, part=self.part1, color=self.color1, qty=1, is_spare=False)
        self.set_part2 = SetPart.objects.create(
            set_inventory=1, part=self.part1, color=self.color2, qty=1, is_spare=False)

    def test_colors_single_user(self):
        # No Color
        self.assertEqual(self.user_part1.used_colors.count(), 0)

        # 1 Cplor
        Inventory.objects.create(userpart=self.user_part1, color=self.color1, qty=1)
        result = self.user_part1.used_colors
        self.assertEqual(result.count(), 1)
        self.assertTrue(result.filter(name=self.color1.name).exists())

    def test_colors_multi_user(self):
        Inventory.objects.create(userpart=self.user_part1, color=self.color1, qty=1)
        Inventory.objects.create(userpart=self.user_part1, color=self.color2, qty=1)
        Inventory.objects.create(userpart=self.user_part1, color=self.color3, qty=1)
        Inventory.objects.create(userpart=self.user_part2, color=self.color2, qty=1)

        result = self.user_part1.used_colors
        self.assertEqual(result.count(), 3)
        self.assertTrue(result.filter(name=self.color1.name).exists())
        self.assertTrue(result.filter(name=self.color2.name).exists())
        self.assertTrue(result.filter(name=self.color3.name).exists())

        result = self.user_part2.used_colors
        self.assertEqual(result.count(), 1)
        self.assertTrue(result.filter(name=self.color2.name).exists())

    def test_available_colors_to_select(self):
        Inventory.objects.create(userpart=self.user_part1, color=self.color1, qty=1)

        # 1 and 2 are available, 3 is not
        result = self.user_part1.unused_colors
        self.assertEqual(result.count(), 1)
        self.assertTrue(result.filter(name=self.color2.name).exists())

class TestInventoryQty(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(  # nosec
            username='User', email='jacob@…', password='top_secret')

        self.part_category = PartCategory.objects.create(id=1, name='category')

        self.part = Part.objects.create(
            part_num='Part', name='A Part', category=self.part_category)

        self.user_part = UserPart.objects.create(user=self.user, part=self.part)

        self.color_red = Color.objects.create(id=4, name='Red', rgb='C91A09')
        self.color_black = Color.objects.create(id=20, name='Black', rgb='000000')
        self.color_white = Color.objects.create(id=50, name='White', rgb='FFFFFF')

    def test_no_colors_0_qty(self):
        self.assertEqual(self.user_part.inventory_count, 0)

    def test_colors_with_0_qty(self):
        # Add a first Color
        Inventory.objects.create(userpart=self.user_part, color=self.color_red, qty=0)
        self.assertEqual(self.user_part.used_colors.count(), 1)
        self.assertEqual(self.user_part.inventory_count, 0)

        # Add a second color
        Inventory.objects.create(userpart=self.user_part, color=self.color_black, qty=0)
        self.assertEqual(self.user_part.used_colors.count(), 2)
        self.assertEqual(self.user_part.inventory_count, 0)

    def test_color_with_qty(self):
        Inventory.objects.create(userpart=self.user_part, color=self.color_red, qty=15)
        self.assertEqual(self.user_part.used_colors.count(), 1)
        self.assertEqual(self.user_part.inventory_count, 15)

    def test_multiple_colors_mixed_qty(self):
        Inventory.objects.create(userpart=self.user_part, color=self.color_red, qty=0)
        Inventory.objects.create(userpart=self.user_part, color=self.color_black, qty=2)
        Inventory.objects.create(userpart=self.user_part, color=self.color_white, qty=8)
        self.assertEqual(self.user_part.used_colors.count(), 3)
        self.assertEqual(self.user_part.inventory_count, 10)

    def test_multiple_userpart_same_color(self):
        self.part2 = Part.objects.create(
            part_num='PartB', name='B Part', category=self.part_category)
        self.user_part2 = UserPart.objects.create(user=self.user, part=self.part2)

        Inventory.objects.create(userpart=self.user_part, color=self.color_red, qty=2)
        Inventory.objects.create(userpart=self.user_part2, color=self.color_red, qty=4)

        self.assertEqual(self.user_part.used_colors.count(), 1)
        self.assertEqual(self.user_part.inventory_count, 2)

        self.assertEqual(self.user_part2.used_colors.count(), 1)
        self.assertEqual(self.user_part2.inventory_count, 4)
