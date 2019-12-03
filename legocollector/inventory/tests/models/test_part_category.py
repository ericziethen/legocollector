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

    '''
    def test_height_for_category(self):
        category1 = PartCategory.objects.create(name='Plates')



        category2 = PartCategory.objects.create(name='Tiles')
    '''