from django.test import TestCase


# Create your tests here.
class MathTest(TestCase):
    """Этот класс я создал чтобы тестировать настройку CI/CD"""

    def test_some_math(self):
        """Эта функция - пустой тест. Нужна чтобы я мог тестировать CI/CD"""
        self.assertEqual(2 / 1, 2)
        self.assertEqual(0 / 2, 0)
