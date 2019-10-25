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
        self.assertEqual(part.related_part_count(), 0)

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

    def test_related_parte(self):
        part1of3 = Part.objects.get(part_num='part1of3')
        part2of3 = Part.objects.get(part_num='part2of3')
        part3of3 = Part.objects.get(part_num='part3of3')

        part1_related = part1of3.get_related_parts()
        part2_related = part2of3.get_related_parts()
        part3_related = part3of3.get_related_parts()

        self.assertListEqual(part1_related, [part2of3, part3of3])
        self.assertListEqual(part2_related, [part3of3, part1of3])
        self.assertListEqual(part3_related, [part2of3, part1of3])

        self.assertIn(part2of3, part1_related)
        self.assertIn(part3of3, part1_related)
        self.assertIn(part1of3, part2_related)
        self.assertIn(part3of3, part2_related)
        self.assertIn(part1of3, part3_related)
        self.assertIn(part2of3, part3_related)

    def test_related_part_count(self):
        part1of3 = Part.objects.get(part_num='part1of3')
        part2of3 = Part.objects.get(part_num='part2of3')
        part3of3 = Part.objects.get(part_num='part3of3')

        self.assertEqual(part1of3.related_part_count(), 2)
        self.assertEqual(part2of3.related_part_count(), 2)
        self.assertEqual(part3of3.related_part_count(), 2)

    def test_children_circular(self):
        part1of3 = Part.objects.get(part_num='part1of3')
        part2of3 = Part.objects.get(part_num='part2of3')
        part3of3 = Part.objects.get(part_num='part3of3')
        PartRelationship.objects.create(parent_part=part3of3, child_part=part1of3,
                                        relationship_type=PartRelationship.ALTERNATE_PART)

        children = part1of3.get_children()
        parents = part1of3.get_parents()
        related = part1of3.get_related_parts()

        self.assertListEqual(children, [part2of3, part3of3])
        self.assertListEqual(parents, [part3of3, part2of3])
        self.assertListEqual(related, [part2of3, part3of3])

        self.assertIn(part2of3, children)
        self.assertIn(part3of3, children)
        self.assertIn(part2of3, parents)
        self.assertIn(part3of3, parents)
        self.assertIn(part2of3, related)
        self.assertIn(part3of3, related)

        self.assertEqual(part1of3.related_part_count(), 2)
