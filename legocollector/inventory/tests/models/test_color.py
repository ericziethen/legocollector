from django.test import TestCase

from inventory.models import Color


class TestColorCreation(TestCase):  # pylint: disable=too-many-instance-attributes

    def setUp(self):
        self.color_red = Color.objects.create(id='4', name='Red', rgb='C91A09')

    def test_colorcreation(self):
        self.assertFalse(self.color_red.transparent)
        self.assertEqual(self.color_red.id, '4')
        self.assertEqual(self.color_red.name, 'Red')
        self.assertEqual(self.color_red.rgb, 'C91A09')
        self.assertEqual(self.color_red.rgb_ints, (201, 26, 9))
        self.assertEqual(self.color_red.complimentary_color, 'FFFFFF')
        self.assertEqual(self.color_red.color_step_hue, 0)
        self.assertAlmostEqual(self.color_red.color_step_lumination, 8.18651329932347, places=14, msg=None, delta=None)
        self.assertEqual(self.color_red.color_step_value, 1608)
