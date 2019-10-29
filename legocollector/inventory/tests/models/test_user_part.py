from django.contrib.auth.models import User
from django.test import TestCase

from inventory.models import Color, Inventory, Part, PartCategory, UserPart

class TestInventoryColors(TestCase):

    def setUp(self):
        self.user1 = User.objects.create_user(
            username='jacob', email='jacob@…', password='top_secret')

        self.part_category1 = PartCategory.objects.create(name='category1')

        # TODO - If this fails, then h l v values might need to have defaults of 0
        self.color1 = Color(id='ColorIdRed', name='Red', rgb='AAAAAA')
        self.color1 = Color(id='ColorIdBlue', name='Blue', rgb='BBBBBB')
        self.color1 = Color(id='ColorIdGreen', name='Green', rgb='CCCCCC')

        self.part1 = Part(part_num='PartA', name='A Part', category=self.part_category1)

        self.user_part1 = UserPart(user=self.user1, part=self.part1)


    ''' TODO - Tests to do
        - no color set
        - some colors set
        - all colors set
        - available colors to select (TODO - This function/property will replace the current form calculation)



    '''

