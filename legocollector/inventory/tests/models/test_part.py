from django.test import TestCase

from inventory.models import Color, Part, PartCategory, PartRelationship, SetPart


class TestGetRelatedParts(TestCase):

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


class TestAvailableColors(TestCase):

    def setUp(self):
        self.part_category1 = PartCategory.objects.create(id=1, name='category1')

        self.color1 = Color.objects.create(id='1', name='Red', rgb='AAAAAA')
        self.color2 = Color.objects.create(id='2', name='Blue', rgb='BBBBBB')
        self.color3 = Color.objects.create(id='3', name='Green', rgb='CCCCCC')

        self.part1 = Part.objects.create(
            part_num='PartA', name='A Part', category=self.part_category1)

        self.set_part1 = SetPart.objects.create(
            set_inventory=1, part=self.part1, color=self.color1, qty=1, is_spare=False)
        self.set_part2 = SetPart.objects.create(
            set_inventory=1, part=self.part1, color=self.color2, qty=1, is_spare=False)

    def test_available_colors(self):
        result = self.part1.available_colors
        self.assertEqual(result.count(), 2)
        self.assertTrue(result.filter(name=self.color1.name).exists())
        self.assertTrue(result.filter(name=self.color2.name).exists())


class TestDimensions(TestCase):

    def setUp(self):
        self.part_category1 = PartCategory.objects.create(id=1, name='category1')

    def test_dimension_no_attribs(self):
        part = Part.objects.create(
            part_num='PartA', name='A Part', category=self.part_category1)
        self.assertEqual(part.dimension_set_count, 0)

    def test_dimension_single_attribs(self):
        part = Part.objects.create(
            part_num='Part1', name='A Part', category=self.part_category1, width=1)
        self.assertEqual(part.dimension_set_count, 1)
        part = Part.objects.create(
            part_num='Part2', name='A Part', category=self.part_category1, height=1)
        self.assertEqual(part.dimension_set_count, 1)
        part = Part.objects.create(
            part_num='Part3', name='A Part', category=self.part_category1, length=1)
        self.assertEqual(part.dimension_set_count, 1)

    def test_dimension_2_attribs(self):
        part = Part.objects.create(
            part_num='PartA', name='A Part', category=self.part_category1, width=1, length=3)
        self.assertEqual(part.dimension_set_count, 2)

    def test_dimension_all_attribs(self):
        part = Part.objects.create(
            part_num='PartA', name='A Part', category=self.part_category1, width=1, height=15, length=3)
        self.assertEqual(part.dimension_set_count, 3)

class TestStuds(TestCase):

    def setUp(self):
        self.part_category1 = PartCategory.objects.create(id=1, name='category1')

    def test_studs_no_attribs(self):
        part = Part.objects.create(
            part_num='PartA', name='A Part', category=self.part_category1)
        self.assertEqual(part.studs_set_count, 0)

    def test_studs_single_attribs(self):
        part = Part.objects.create(
            part_num='Part1', name='A Part', category=self.part_category1, top_studs=1)
        self.assertEqual(part.studs_set_count, 1)
        part = Part.objects.create(
            part_num='Part2', name='A Part', category=self.part_category1, bottom_studs=1)
        self.assertEqual(part.studs_set_count, 1)
        part = Part.objects.create(
            part_num='Part3', name='A Part', category=self.part_category1, stud_rings=1)
        self.assertEqual(part.studs_set_count, 1)

    def test_studs_2_attribs(self):
        part = Part.objects.create(
            part_num='PartA', name='A Part', category=self.part_category1, top_studs=1, stud_rings=3)
        self.assertEqual(part.studs_set_count, 2)

    def test_studs_all_attribs(self):
        part = Part.objects.create(
            part_num='PartA', name='A Part', category=self.part_category1, top_studs=1, bottom_studs=15, stud_rings=3)
        self.assertEqual(part.studs_set_count, 3)

    def test_swap_width_and_length(self):
        part = Part.objects.create(
            part_num='PartA', name='A Part', category=self.part_category1, width=20, height=15, length=5)
        self.assertEqual(part.width, 5)
        self.assertEqual(part.length, 20)
        self.assertEqual(part.height, 15)
