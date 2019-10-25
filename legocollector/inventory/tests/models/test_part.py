from django.test import TestCase

from inventory.models import Part, PartCategory, PartRelationship


class PartTests(TestCase):

    def setUp(self):
        PartCategory.objects.create(name='category1')

        Part.objects.create(part_num='single_part', name='single_part',
                            category=PartCategory.objects.get(name='category1'))

        ''' Relationships for Testing
            |-1   B
            | |  /
            | 2 A
            | |/ \
            |-3   C

            |-X
            | |
            | Y
            | |
            |-Z



        '''

        Part.objects.create(part_num='1', name='1',
                            category=PartCategory.objects.get(name='category1'))

        Part.objects.create(part_num='2', name='2',
                            category=PartCategory.objects.get(name='category1'))

        Part.objects.create(part_num='3', name='3',
                            category=PartCategory.objects.get(name='category1'))

        Part.objects.create(part_num='A', name='A',
                            category=PartCategory.objects.get(name='category1'))

        Part.objects.create(part_num='B', name='B',
                            category=PartCategory.objects.get(name='category1'))

        Part.objects.create(part_num='C', name='C',
                            category=PartCategory.objects.get(name='category1'))

        Part.objects.create(part_num='X', name='X',
                            category=PartCategory.objects.get(name='category1'))

        Part.objects.create(part_num='Y', name='Y',
                            category=PartCategory.objects.get(name='category1'))

        Part.objects.create(part_num='Z', name='Z',
                            category=PartCategory.objects.get(name='category1'))

        PartRelationship.objects.create(
            parent_part=Part.objects.get(part_num='1'),
            child_part=Part.objects.get(part_num='2'),
            relationship_type=PartRelationship.ALTERNATE_PART)

        PartRelationship.objects.create(
            parent_part=Part.objects.get(part_num='2'),
            child_part=Part.objects.get(part_num='3'),
            relationship_type=PartRelationship.ALTERNATE_PART)

        PartRelationship.objects.create(
            parent_part=Part.objects.get(part_num='3'),
            child_part=Part.objects.get(part_num='1'),
            relationship_type=PartRelationship.ALTERNATE_PART)

        PartRelationship.objects.create(
            parent_part=Part.objects.get(part_num='A'),
            child_part=Part.objects.get(part_num='3'),
            relationship_type=PartRelationship.ALTERNATE_PART)

        PartRelationship.objects.create(
            parent_part=Part.objects.get(part_num='A'),
            child_part=Part.objects.get(part_num='C'),
            relationship_type=PartRelationship.ALTERNATE_PART)

        PartRelationship.objects.create(
            parent_part=Part.objects.get(part_num='B'),
            child_part=Part.objects.get(part_num='A'),
            relationship_type=PartRelationship.ALTERNATE_PART)

        PartRelationship.objects.create(
            parent_part=Part.objects.get(part_num='X'),
            child_part=Part.objects.get(part_num='Y'),
            relationship_type=PartRelationship.ALTERNATE_PART)

        PartRelationship.objects.create(
            parent_part=Part.objects.get(part_num='Y'),
            child_part=Part.objects.get(part_num='Z'),
            relationship_type=PartRelationship.ALTERNATE_PART)

        PartRelationship.objects.create(
            parent_part=Part.objects.get(part_num='Z'),
            child_part=Part.objects.get(part_num='X'),
            relationship_type=PartRelationship.ALTERNATE_PART)

    def test_related_parts_all_args_false(self):
        part_a = Part.objects.get(part_num='A')

        self.assertListEqual(part_a.get_related_parts(parents=False, children=False, transitive=False), [])
        self.assertEqual(part_a.related_part_count(parents=False, children=False, transitive=False), 0)

    def test_related_parts_no_parents(self):
        part_b = Part.objects.get(part_num='B')
        self.assertListEqual(part_b.get_related_parts(parents=True, children=False, transitive=True), [])

    def test_related_1_parent(self):
        part_a = Part.objects.get(part_num='A')
        part_b = Part.objects.get(part_num='B')
        part_c = Part.objects.get(part_num='C')

        self.assertListEqual(part_a.get_related_parts(parents=True, children=False, transitive=False), [part_b])
        self.assertListEqual(part_c.get_related_parts(parents=True, children=False, transitive=False), [part_a])
        self.assertListEqual(part_a.get_related_parts(parents=True, children=False, transitive=True), [part_b])

    def test_related_transitive_parent(self):
        part_a = Part.objects.get(part_num='A')
        part_b = Part.objects.get(part_num='B')
        part_c = Part.objects.get(part_num='C')

        parents = part_c.get_related_parts(parents=True, children=False, transitive=True)
        self.assertEqual(len(parents), 2)
        self.assertIn(part_a, parents)
        self.assertIn(part_b, parents)

    def test_related_transitive_parent_circular(self):
        part_x = Part.objects.get(part_num='X')
        part_y = Part.objects.get(part_num='Y')
        part_z = Part.objects.get(part_num='Z')

        parents = part_x.get_related_parts(parents=True, children=False, transitive=True)
        self.assertEqual(len(parents), 2)
        self.assertIn(part_y, parents)
        self.assertIn(part_z, parents)
    '''
    def test_related_parts_no_children(self):
        part_c = Part.objects.get(part_num='C')
        self.assertListEqual(part_c.get_related_parts(parents=False, children=True, transitive=True), [])
    '''
    '''

    def test_related_parts_children_only(self):

    def test_related_parts_parents_and_children(self):

    def test_related_parts_parents_transitive(self):

    def test_related_parts_children_transitive(self):

    def test_related_parts_parents_children_transitive(self):
    '''

























    '''
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
    '''