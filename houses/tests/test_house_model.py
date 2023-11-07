from django.core.exceptions import ValidationError
from django.test import TestCase

from core.models import Pricing
from houses.models import House


class HouseModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создаём тестовую запись в БД
        # и сохраняем созданную запись в качестве переменной класса
        cls.house = House.objects.create(
            name='Тестовый домик',
            description='Тестовое описание',
        )

    def test_unique_house_name(self):
        with self.assertRaises(ValidationError, msg="Создано 2 домика с одинаковыми именами"):
            house1 = House.objects.create(
                name='Домик',
                description='Тестовое описание1',
            )
            House.objects.create(
                name=house1.name,
                description='Тестовое описание2',
            )

    def test_verbose_name(self):
        """verbose_name в полях совпадает с ожидаемым."""
        house = HouseModelTest.house

        field_verboses = {
            'name': "Название домика",

            'description': "Описание домика",
            'features': "Плюшки",

            'base_price': "Базовая цена",
            'holidays_multiplier': "Множитель в выходные и праздники",

            'base_persons_amount': 'Базовое количество человек для проживания в домике',
            'max_persons_amount': 'Максимальное количество человек для проживания в домике',
            'price_per_extra_person': 'Цена за дополнительного человека',

            'created_at': "Время создания домика",
            'updated_at': "Время последнего изменения домика",
        }

        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(house._meta.get_field(field).verbose_name, expected_value)

    def test_base_price_validators(self):
        for base_price_test_value in [-100, -1, 0, 1, 100, Pricing.MIN_HOUSE_BASE_PRICE - 1]:
            with self.assertRaises(ValidationError,
                                   msg=f"Создан домик с базовой ценой {base_price_test_value}, "
                                       f"при минимальной {Pricing.MIN_HOUSE_BASE_PRICE}"):
                house = House.objects.create(
                    name='Домик',
                    description='Тестовое описание',
                    holidays_multiplier=1,
                    base_price=base_price_test_value,
                )
                house.delete()

        # проверка, что можно создать домик с минимальной ценой
        try:
            house = House.objects.create(
                name='Домик',
                description='Тестовое описание',
                holidays_multiplier=1,
                base_price=Pricing.MIN_HOUSE_BASE_PRICE,
            )
        except ValidationError:
            self.fail(msg=f"Не удалось создать домик с базовой ценой {Pricing.MIN_HOUSE_BASE_PRICE}, "
                          f"при минимальной {Pricing.MIN_HOUSE_BASE_PRICE}")

    def test_holidays_multiplier_default_value(self):
        house = House.objects.create(
            name='Домик',
            description='Тестовое описание',
        )

        self.assertEqual(house.holidays_multiplier, 2)

    def test_holidays_base_price_default_value(self):
        house = House.objects.create(
            name='Тестовый домик 2',
            description='Тестовое описание',
        )

        self.assertEqual(house.base_price, 10000)

    def test_holidays_multiplier_validators(self):
        self.assertTrue(Pricing.MIN_HOUSE_HOLIDAYS_MULTIPLIER >= 1,
                        "Множитель должен увеличивать базовую цену в выходные дни")

        for holiday_multiplier_test_value in [-100, -1, 0, Pricing.MIN_HOUSE_HOLIDAYS_MULTIPLIER - 0.0001]:
            with self.assertRaises(ValidationError,
                                   msg=f"Создан домик с множителем {holiday_multiplier_test_value}, "
                                       f"при минимальной {Pricing.MIN_HOUSE_HOLIDAYS_MULTIPLIER}"):
                house = House.objects.create(
                    name='Домик',
                    description='Тестовое описание',
                    holidays_multiplier=holiday_multiplier_test_value,
                )
                house.delete()

        # проверка, что можно создать домик с минимальной ценой
        try:
            house = House.objects.create(
                name='Домик',
                description='Тестовое описание',
                holidays_multiplier=Pricing.MIN_HOUSE_HOLIDAYS_MULTIPLIER,
            )
        except ValidationError:
            self.fail(msg=f"Не удалось создать домик с множителем {Pricing.MIN_HOUSE_HOLIDAYS_MULTIPLIER}, "
                          f"при минимальной {Pricing.MIN_HOUSE_HOLIDAYS_MULTIPLIER}")
