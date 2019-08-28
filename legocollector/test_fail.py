from django.test import TestCase

class TestFail(TestCase):

    def test_FAIL(self):
        self.assertTrue(False)
