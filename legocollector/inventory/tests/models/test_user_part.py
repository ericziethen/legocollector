from django.contrib.auth.models import User
from django.test import TestCase

from inventory.models import Color, Inventory, Part, PartCategory, SetPart, UserPart


class TestInventoryColors(TestCase):

    def setUp(self):
        print('run')
        self.user1 = User.objects.create_user(
            username='User1', email='jacob@…', password='top_secret')
        self.user2 = User.objects.create_user(
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
