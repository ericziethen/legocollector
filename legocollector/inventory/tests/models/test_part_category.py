from django.test import TestCase
from parameterized import parameterized

from inventory.models import PartCategory


class TestPartCategoryHeight(TestCase):

    @parameterized.expand([
        ('category1'),
        ('Baseplates'),
        ('Bricks'),
        ('Plates Special'),
        ('Plates Round and Dishes'),
        ('Plates Angled'),
        ('Tiles Special'),
    ])
    def test_no_height_for_category(self, category):
        category = PartCategory.objects.create(name=category)
        self.assertIsNone(category.height)

    @parameterized.expand([
        ('Plates'),
        ('Tiles'),
    ])
    def test_height_for_category(self, name):
        category = PartCategory.objects.create(name=name)
        self.assertEqual(category.height, 0.33)
