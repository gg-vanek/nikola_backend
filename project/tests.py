from django.test import TestCase


# Create your tests here.
class MathTest(TestCase):
    def test_some_math(self):
        self.assertEqual(2 / 1, 2)
        self.assertEqual(0 / 2, 0)
