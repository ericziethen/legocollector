from collections import defaultdict

from django.test import TestCase

from inventory.models import Part, PartCategory, PartRelationship
from inventory.management.commands.set_related_attributes import Command


# TODO - REMOVE after test debugging
import pytest


class TestRelatedAttributes(TestCase):


    def setUp(self):
        self.attribute_updates = defaultdict(int)
        self.conflicting_attribs = {'dimensions': {}, 'top_studs': {}, 'botom_studs': {}, 'stud_rings': {}}

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

    #@staticmethod
    #def assert_part_changes()

    @pytest.mark.eric
    def test_no_dims_no_studs_present(self):
        part1 = Part.objects.get(part_num='part1')
        part2 = Part.objects.get(part_num='part2')
        part3 = Part.objects.get(part_num='part3')

        Command.set_related_attribs_for_part(
            part1, attribute_updates=self.attribute_updates, conflicting_attribs=self.conflicting_attribs)

        self.assertEqual(part1.dimension_set_count, 0)
        self.assertEqual(part2.dimension_set_count, 0)
        self.assertEqual(part3.dimension_set_count, 0)

        self.assertEqual(part1.studs_set_count, 0)
        self.assertEqual(part2.studs_set_count, 0)
        self.assertEqual(part3.studs_set_count, 0)

    @pytest.mark.eric
    def test_set_width(self):
        part1 = Part.objects.get(part_num='part1')
        part2 = Part.objects.get(part_num='part2')
        part3 = Part.objects.get(part_num='part3')

        part2.width = 10
        part2.save()

        Command.set_related_attribs_for_part(
            part1, attribute_updates=self.attribute_updates, conflicting_attribs=self.conflicting_attribs)

        part1 = Part.objects.get(part_num='part1')
        part2 = Part.objects.get(part_num='part2')
        part3 = Part.objects.get(part_num='part3')

        self.assertEqual(part1.dimension_set_count, 1)
        self.assertEqual(part2.dimension_set_count, 1)
        self.assertEqual(part3.dimension_set_count, 1)
        self.assertEqual(part1.width, 10)
        self.assertEqual(part2.width, 10)
        self.assertEqual(part3.width, 10)


    '''
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


    def test_parts_processed_updated()

class TestFullCommand(TestCase):

    def setup(self):
        pass

    def test_full_command(self):
        self.assertFalse(True)
        # TODO - Test the overall command
        # https://docs.djangoproject.com/en/2.2/topics/testing/tools/#topics-testing-management-commands
    '''
