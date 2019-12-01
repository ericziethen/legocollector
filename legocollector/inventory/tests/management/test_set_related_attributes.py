from django.test import TestCase

from inventory.models import Color, Part, PartCategory, PartRelationship
#from inventory.management.commands.set_related_attributes.Command import calc_related_attribs


class TestRelatedAttributes(TestCase):

    def setup(self):
        PartCategory.objects.create(name='category1')

        Part.objects.create(part_num='part1', name='part1', category=PartCategory.objects.get(name='category1'))
        Part.objects.create(part_num='part2', name='part2', category=PartCategory.objects.get(name='category1'))
        Part.objects.create(part_num='part3', name='part3', category=PartCategory.objects.get(name='category1'))

        PartRelationship.objects.create(
            parent_part=Part.objects.get(part_num='part1'),
            child_part=Part.objects.get(part_num='part2'),
            relationship_type=PartRelationship.ALTERNATE_PART)

        PartRelationship.objects.create(
            parent_part=Part.objects.get(part_num='part2'),
            child_part=Part.objects.get(part_num='part3'),
            relationship_type=PartRelationship.ALTERNATE_PART)

    '''
    def test_no_dims_no_studs_present(self):
        calc_related_attribs()

        part1 = Part.objects.get(part_num='part1')
        part2 = Part.objects.get(part_num='part2')
        part3 = Part.objects.get(part_num='part3')

        self.assertEqual(part1.dimension_set_count, 0)
        self.assertEqual(part2.dimension_set_count, 0)
        self.assertEqual(part3.dimension_set_count, 0)



        self.assertFalse(True)
    '''
    '''
    def test_set_width(self):
        self.assertFalse(True)

    def test_set_height(self):
        self.assertFalse(True)

    def test_set_length(self):
        self.assertFalse(True)

    def test_set_width_height_length(self):
        self.assertFalse(True)

    def test_clashing_width(self):
        self.assertFalse(True)

    def test_clashing_height(self):
        self.assertFalse(True)

    def test_clashing_length(self):
        self.assertFalse(True)


    def test_set_top_stud(self):
        self.assertFalse(True)

    def test_set_bottom_stud(self):
        self.assertFalse(True)

    def test_set_stud_ring(self):
        self.assertFalse(True)

    def test_clashing_top_stud(self):
        self.assertFalse(True)

    def test_clashing_bottom_stud(self):
        self.assertFalse(True)

    def test_clashing_stud_ring(self):
        self.assertFalse(True)

    def test_clashing_top_stud_others_ok(self):
        self.assertFalse(True)

    def test_clashing_bottom_stud_others_ok(self):
        self.assertFalse(True)

    def test_clashing_stud_ring_others_ok(self):
        self.assertFalse(True)


class TestFullCommand(TestCase):

    def setup(self):
        pass

    def test_full_command(self):
        self.assertFalse(True)
        # TODO - Test the overall command
        # https://docs.djangoproject.com/en/2.2/topics/testing/tools/#topics-testing-management-commands
    '''
