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

    def test_unique_house_name(self):
        try:
            house1 = House.objects.create(
                name='Тестовый домик1',
                description='Тестовое описание1',
                base_price=10000,
                holidays_multiplier=2,
            )
            house2 = House.objects.create(
                name=house1.name,
                description='Тестовое описание2',
                base_price=10000,
                holidays_multiplier=2,
            )
        except ValidationError:
            house1.delete()
        else:
            house1.delete()
            house2.delete()
            assert False, "Создано 2 домика с одинаковыми именами"

    def test_verbose_name(self):
        """verbose_name в полях совпадает с ожидаемым."""
        house = TaskModelTest.house

        field_verboses = {
            'name': "Название домика",
            'description': "Описание домика",
            'base_price': "Базовая цена",
            'holidays_multiplier': "Множитель в выходные и праздники",
            'created_at': "Время создания домика",
            'updated_at': "Время последнего изменения домика",
        }

        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    house._meta.get_field(field).verbose_name, expected_value)

    def test_base_price_validators(self):
        for base_price_test_value in [-100, -1, 0, 1, 100, House.MIN_BASE_PRICE - 1]:
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
                              f"при минимальной {House.MIN_BASE_PRICE}"

        # проверка, что можно создать домик с минимальной ценой
        try:
            house = House.objects.create(
                name='Тестовый домик 1',
                description='Тестовое описание 1',
                holidays_multiplier=1,
                base_price=House.MIN_BASE_PRICE,
            )
        except ValidationError:
            assert False, f"Не удалось создать домик с базовой ценой {base_price_test_value}, " \
                          f"при минимальной {House.MIN_BASE_PRICE}"
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
        base_price_test_value = 100000

        assert House.MIN_HOLIDAYS_MULTIPLIER >= 1, \
            "Множитель должен увеличивать базовую цену в выходные дни"

        for holiday_multiplier_test_value in [-100, -1, 0, House.MIN_HOLIDAYS_MULTIPLIER - 0.0001]:
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
                              f"при минимальной {House.MIN_HOLIDAYS_MULTIPLIER}"

        # проверка, что можно создать домик с минимальной ценой
        try:
            house = House.objects.create(
                name='Тестовый домик 1',
                description='Тестовое описание 1',
                holidays_multiplier=House.MIN_HOLIDAYS_MULTIPLIER,
                base_price=base_price_test_value,
            )
        except ValidationError:
            assert False, \
                f"Не удалось создать домик с множителем {House.MIN_HOLIDAYS_MULTIPLIER}, " \
                f"при минимальной {House.MIN_HOLIDAYS_MULTIPLIER}"
        else:
            house.delete()
