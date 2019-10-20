from django.test import TestCase

from inventory.models import Part, PartCategory, PartRelationship

class PartTests(TestCase):

    def setUp(self):
        PartCategory.objects.create(name='category1')

        Part.objects.create(part_num='single_part', name='single_part',
                            category=PartCategory.objects.get(name='category1'))

        Part.objects.create(part_num='part1of3', name='part1of3',
                            category=PartCategory.objects.get(name='category1'))

        Part.objects.create(part_num='part2of3', name='part2of3',
                            category=PartCategory.objects.get(name='category1'))

        Part.objects.create(part_num='part3of3', name='part3of3',
                            category=PartCategory.objects.get(name='category1'))

        PartRelationship.objects.create(
            parent_part=Part.objects.get(part_num='part1of3'),
            child_part=Part.objects.get(part_num='part2of3'),
            relationship_type=PartRelationship.ALTERNATE_PART)

        PartRelationship.objects.create(
            parent_part=Part.objects.get(part_num='part2of3'),
            child_part=Part.objects.get(part_num='part3of3'),
            relationship_type=PartRelationship.ALTERNATE_PART)

    def test_no_related_parts(self):
        part = Part.objects.get(part_num='single_part')

        self.assertListEqual(part.get_children(), [])
        self.assertListEqual(part.get_parents(), [])
        self.assertListEqual(part.get_related_parts(), [])
        self.assertEquals(part.related_part_count(), 0)

    def test_related_parts(self):
        part1of3 = Part.objects.get(part_num='part1of3')
        part2of3 = Part.objects.get(part_num='part2of3')
        part3of3 = Part.objects.get(part_num='part3of3')

        self.assertEquals(part1of3.related_part_count(), 2)
        self.assertEquals(part2of3.related_part_count(), 2)
        self.assertEquals(part3of3.related_part_count(), 2)

    def test_children(self):
        part1of3 = Part.objects.get(part_num='part1of3')
        part2of3 = Part.objects.get(part_num='part2of3')
        part3of3 = Part.objects.get(part_num='part3of3')

        self.assertListEqual(part1of3.get_children(recursive=False), [part2of3])
        self.assertListEqual(part1of3.get_children(), [part2of3, part3of3])

    def test_parents(self):
        part1of3 = Part.objects.get(part_num='part1of3')
        part2of3 = Part.objects.get(part_num='part2of3')
        part3of3 = Part.objects.get(part_num='part3of3')

        self.assertListEqual(part3of3.get_parents(recursive=False), [part2of3])
        self.assertListEqual(part3of3.get_parents(), [part2of3, part1of3])
    '''
    def test_children_circular(self):
        part1of3 = Part.objects.get(part_num='part1of3')
        part2of3 = Part.objects.get(part_num='part2of3')
        part3of3 = Part.objects.get(part_num='part3of3')
        PartRelationship.objects.create(parent_part=part3of3, child_part=part1of3, 
                                        relationship_type=PartRelationship.ALTERNATE_PART)

        self.assertListEqual(part1of3.get_children(), [part2of3, part3of3])
        self.assertListEqual(part1of3.get_parents(), [part3of3, part2of3])
        self.assertListEqual(part1of3.get_related_parts(), [part2of3, part3of3])
        self.assertEquals(part1of3.related_part_count(), 2)
    '''