from collections import defaultdict

from django.test import TestCase

from inventory.models import Part, PartCategory, PartRelationship
from inventory.management.commands.set_related_attributes import Command


class TestRelatedAttributes(TestCase):

    def setUp(self):
        self.attribute_updates = defaultdict(int)

        PartCategory.objects.create(name='category1')

        self.part1 = Part.objects.create(
            part_num='part1', name='part1', category=PartCategory.objects.get(name='category1'))
        self.part2 = Part.objects.create(
            part_num='part2', name='part2', category=PartCategory.objects.get(name='category1'))
        self.part3 = Part.objects.create(
            part_num='part3', name='part3', category=PartCategory.objects.get(name='category1'))

        PartRelationship.objects.create(
            parent_part=self.part1,
            child_part=self.part2,
            relationship_type=PartRelationship.ALTERNATE_PART)

        PartRelationship.objects.create(
            parent_part=self.part2,
            child_part=self.part3,
            relationship_type=PartRelationship.ALTERNATE_PART)

    def test_no_dims_no_studs_present(self):
        Command.set_related_attribs_for_part(
            self.part1, attribute_updates=self.attribute_updates)

        part1 = Part.objects.get(part_num='part1')
        part2 = Part.objects.get(part_num='part2')
        part3 = Part.objects.get(part_num='part3')

        self.assertEqual(part1.dimension_set_count, 0)
        self.assertEqual(part2.dimension_set_count, 0)
        self.assertEqual(part3.dimension_set_count, 0)

        self.assertEqual(part1.studs_set_count, 0)
        self.assertEqual(part2.studs_set_count, 0)
        self.assertEqual(part3.studs_set_count, 0)

    def test_copy_attributes(self):
        self.part1.width = 10
        self.part1.top_studs = 100
        self.part1.image_url = 'www.image_url.com'
        self.part1.save()

        self.part2.height = 20
        self.part2.bottom_studs = 200
        self.part2.save()

        self.part3.length = 30
        self.part3.stud_rings = 300
        self.part3.save()

        Command.set_related_attribs_for_part(
            self.part1, attribute_updates=self.attribute_updates)

        part1 = Part.objects.get(part_num='part1')
        part2 = Part.objects.get(part_num='part2')
        part3 = Part.objects.get(part_num='part3')

        self.assertEqual(part1.dimension_set_count, 3)
        self.assertEqual(part2.dimension_set_count, 3)
        self.assertEqual(part3.dimension_set_count, 3)

        self.assertEqual(part1.width, 10)
        self.assertEqual(part2.width, 10)
        self.assertEqual(part3.width, 10)

        self.assertEqual(part1.height, 20)
        self.assertEqual(part2.height, 20)
        self.assertEqual(part3.height, 20)

        self.assertEqual(part1.length, 30)
        self.assertEqual(part2.length, 30)
        self.assertEqual(part3.length, 30)

        self.assertEqual(part1.top_studs, 100)
        self.assertEqual(part2.top_studs, 100)
        self.assertEqual(part3.top_studs, 100)

        self.assertEqual(part1.bottom_studs, 200)
        self.assertEqual(part2.bottom_studs, 200)
        self.assertEqual(part3.bottom_studs, 200)

        self.assertEqual(part1.stud_rings, 300)
        self.assertEqual(part2.stud_rings, 300)
        self.assertEqual(part3.stud_rings, 300)

        self.assertEqual(part1.image_url, 'www.image_url.com')
        self.assertEqual(part2.image_url, 'www.image_url.com')
        self.assertEqual(part3.image_url, 'www.image_url.com')

        self.assertEqual(self.attribute_updates['total_parts'], 3)

    def test_clashing_values(self):
        self.part1.width = 10
        self.part1.height = 20
        self.part1.top_studs = 100
        self.part1.image_url = 'www.image_url.com'
        self.part1.save()

        self.part2.width = 100
        self.part2.bottom_studs = 200
        self.part2.save()

        self.part3.length = 30
        self.part3.bottom_studs = 300
        self.part3.save()

        Command.set_related_attribs_for_part(
            self.part1, attribute_updates=self.attribute_updates)

        part1 = Part.objects.get(part_num='part1')
        part2 = Part.objects.get(part_num='part2')
        part3 = Part.objects.get(part_num='part3')

        self.assertEqual(part1.dimension_set_count, 3)
        self.assertEqual(part2.dimension_set_count, 3)
        self.assertEqual(part3.dimension_set_count, 3)

        self.assertEqual(part1.width, 10)
        self.assertEqual(part2.width, 30)
        self.assertEqual(part3.width, 10)

        self.assertEqual(part1.height, 20)
        self.assertEqual(part2.height, 20)
        self.assertEqual(part3.height, 20)

        self.assertEqual(part1.length, 30)
        self.assertEqual(part2.length, 100)
        self.assertEqual(part3.length, 30)

        self.assertEqual(part1.top_studs, 100)
        self.assertEqual(part2.top_studs, 100)
        self.assertEqual(part3.top_studs, 100)

        self.assertEqual(part1.bottom_studs, 200)
        self.assertEqual(part2.bottom_studs, 200)
        self.assertEqual(part3.bottom_studs, 300)

        self.assertEqual(part1.stud_rings, None)
        self.assertEqual(part2.stud_rings, None)
        self.assertEqual(part3.stud_rings, None)

        self.assertEqual(part1.image_url, 'www.image_url.com')
        self.assertEqual(part2.image_url, 'www.image_url.com')
        self.assertEqual(part3.image_url, 'www.image_url.com')
