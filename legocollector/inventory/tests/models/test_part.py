from django.test import TestCase

from inventory.models import Part, PartCategory, PartRelationship


class GetRelatedPartsTests(TestCase):

    def setUp(self):
        PartCategory.objects.create(name='category1')

        Part.objects.create(part_num='single_part', name='single_part',
                            category=PartCategory.objects.get(name='category1'))

        # pylint: disable=pointless-string-statement
        '''
            Relationships for Testing
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

    def test_related_parts_no_children(self):
        part_c = Part.objects.get(part_num='C')
        self.assertListEqual(part_c.get_related_parts(parents=False, children=True, transitive=True), [])

    def test_related_1_child(self):
        part_1 = Part.objects.get(part_num='1')
        part_2 = Part.objects.get(part_num='2')
        part_3 = Part.objects.get(part_num='3')

        self.assertListEqual(part_1.get_related_parts(parents=False, children=True, transitive=False), [part_2])
        self.assertListEqual(part_2.get_related_parts(parents=False, children=True, transitive=False), [part_3])
        self.assertListEqual(part_2.get_related_parts(parents=False, children=True, transitive=True), [part_3])

    def test_related_transitive_children(self):
        part_1 = Part.objects.get(part_num='1')
        part_2 = Part.objects.get(part_num='2')
        part_3 = Part.objects.get(part_num='3')

        parents = part_1.get_related_parts(parents=False, children=True, transitive=True)
        self.assertEqual(len(parents), 2)
        self.assertIn(part_2, parents)
        self.assertIn(part_3, parents)

    def test_related_transitive_children_circular(self):
        part_x = Part.objects.get(part_num='X')
        part_y = Part.objects.get(part_num='Y')
        part_z = Part.objects.get(part_num='Z')

        parents = part_x.get_related_parts(parents=False, children=True, transitive=True)
        self.assertEqual(len(parents), 2)
        self.assertIn(part_y, parents)
        self.assertIn(part_z, parents)

    def test_related_1_child_1_parent(self):
        part_1 = Part.objects.get(part_num='1')
        part_2 = Part.objects.get(part_num='2')
        part_3 = Part.objects.get(part_num='3')

        parents = part_2.get_related_parts(parents=True, children=True, transitive=False)
        self.assertEqual(len(parents), 2)
        self.assertIn(part_1, parents)
        self.assertIn(part_3, parents)

    def test_all_related_parts_transitive(self):
        part_1 = Part.objects.get(part_num='1')
        part_2 = Part.objects.get(part_num='2')
        part_3 = Part.objects.get(part_num='3')
        part_a = Part.objects.get(part_num='A')
        part_b = Part.objects.get(part_num='B')
        part_c = Part.objects.get(part_num='C')

        part_list = [part_1, part_2, part_3, part_a, part_b, part_c]

        related_parts = part_1.get_related_parts(parents=True, children=True, transitive=True)
        self.assertEqual(
            sorted(related_parts, key=lambda p: p.part_num),
            sorted([part_2, part_3, part_a, part_b, part_c], key=lambda p: p.part_num))
        self.assertEqual(part_1.related_part_count(parents=True, children=True, transitive=True), 5)

        for part in part_list:
            target_list = part_list.copy()
            target_list.remove(part)

            related_parts = part.get_related_parts(parents=True, children=True, transitive=True)
            self.assertEqual(len(related_parts), 5)
            for target in target_list:
                self.assertIn(target, related_parts)
