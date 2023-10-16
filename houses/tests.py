from django.core.exceptions import ValidationError
from django.test import TestCase
from houses.models import House


class TaskModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создаём тестовую запись в БД
        # и сохраняем созданную запись в качестве переменной класса
        cls.house = House.objects.create(
            name='Тестовый домик',
            description='Тестовое описание',
            base_price=10000,
            holidays_multiplier=2,
        )

    def test_verbose_name(self):
        """verbose_name в полях совпадает с ожидаемым."""
        house = TaskModelTest.house

        field_verboses = {
            'name': "Название домика",
            'description': "Описание домика",
            'base_price': "Базовая цена",
            'holidays_multiplier': "Множитель в выходные и праздники",
            'created_at': "Время создания",
            'updated_at': "Время последнего изменения",
        }

        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    house._meta.get_field(field).verbose_name, expected_value)

    def test_base_price_validators(self):
        min_base_price_value = 1000

        for base_price_test_value in [-100, -1, 0, 1, 100, min_base_price_value - 1]:
            try:
                house = House.objects.create(
                    name='Тестовый домик 1',
                    description='Тестовое описание 1',
                    holidays_multiplier=1,
                    base_price=base_price_test_value,
                )
            except ValidationError:
                continue
            else:
                house.delete()
                assert False, f"Создан домик с базовой ценой {base_price_test_value}, " \
                              f"при минимальной {min_base_price_value}"

        # проверка, что можно создать домик с минимальной ценой
        try:
            house = House.objects.create(
                name='Тестовый домик 1',
                description='Тестовое описание 1',
                holidays_multiplier=1,
                base_price=min_base_price_value,
            )
        except ValidationError:
            assert False, f"Не удалось создать домик с базовой ценой {base_price_test_value}, " \
                          f"при минимальной {min_base_price_value}"
        else:
            house.delete()

    def test_holidays_multiplier_default_value(self):
        house = House.objects.create(
            name='Тестовый домик 2',
            description='Тестовое описание 2',
            base_price=20000,
        )
        self.assertEqual(house.holidays_multiplier, 1)
        house.delete()

    def test_holidays_multiplier_validators(self):
        min_holiday_multiplier_value = 1
        base_price_test_value = 100000

        assert min_holiday_multiplier_value >= 1, \
            "Множитель должен увеличивать базовую цену в выходные дни"

        for holiday_multiplier_test_value in [-100, -1, 0, min_holiday_multiplier_value - 0.0001]:
            try:
                house = House.objects.create(
                    name='Тестовый домик 1',
                    description='Тестовое описание 1',
                    holidays_multiplier=holiday_multiplier_test_value,
                    base_price=base_price_test_value,
                )
            except ValidationError:
                continue
            else:
                house.delete()
                assert False, f"Создан домик с множителем {holiday_multiplier_test_value}, " \
                              f"при минимальной {min_holiday_multiplier_value}"

        # проверка, что можно создать домик с минимальной ценой
        try:
            house = House.objects.create(
                name='Тестовый домик 1',
                description='Тестовое описание 1',
                holidays_multiplier=min_holiday_multiplier_value,
                base_price=base_price_test_value,
            )
        except ValidationError:
            assert False, \
                f"Не удалось создать домик с множителем {min_holiday_multiplier_value}, " \
                f"при минимальной {min_holiday_multiplier_value}"
        else:
            house.delete()
