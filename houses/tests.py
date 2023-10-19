from datetime import timedelta

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils.timezone import now

from clients.models import Client
from core.models import Pricing
from houses.models import House, HouseReservation


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
        try:
            house1 = House.objects.create(
                name='Тестовый домик1',
                description='Тестовое описание1',
            )
            House.objects.create(
                name=house1.name,
                description='Тестовое описание2',
            )
        except ValidationError:
            pass
        else:
            assert False, "Создано 2 домика с одинаковыми именами"

    def test_verbose_name(self):
        """verbose_name в полях совпадает с ожидаемым."""
        house = HouseModelTest.house

        field_verboses = {
            'name': "Название домика",
            'description': "Описание домика",
            'features': "Плюшки",
            "max_occupancy": "Максимальное количество человек для проживания в домике",
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
        for base_price_test_value in [-100, -1, 0, 1, 100, Pricing.MIN_HOUSE_BASE_PRICE - 1]:
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
                              f"при минимальной {Pricing.MIN_HOUSE_BASE_PRICE}"

        # проверка, что можно создать домик с минимальной ценой
        try:
            house = House.objects.create(
                name='Тестовый домик 1',
                description='Тестовое описание 1',
                holidays_multiplier=1,
                base_price=Pricing.MIN_HOUSE_BASE_PRICE,
            )
        except ValidationError:
            assert False, f"Не удалось создать домик с базовой ценой {Pricing.MIN_HOUSE_BASE_PRICE}, " \
                          f"при минимальной {Pricing.MIN_HOUSE_BASE_PRICE}"

    def test_holidays_multiplier_default_value(self):
        house = House.objects.create(
            name='Тестовый домик 2',
            description='Тестовое описание 2',
        )

        self.assertEqual(house.holidays_multiplier, 2)

    def test_holidays_base_price_default_value(self):
        house = House.objects.create(
            name='Тестовый домик 2',
            description='Тестовое описание 2',
        )

        self.assertEqual(house.base_price, 10000)

    def test_holidays_multiplier_validators(self):
        assert Pricing.MIN_HOUSE_HOLIDAYS_MULTIPLIER >= 1, \
            "Множитель должен увеличивать базовую цену в выходные дни"

        for holiday_multiplier_test_value in [-100, -1, 0, Pricing.MIN_HOUSE_HOLIDAYS_MULTIPLIER - 0.0001]:
            try:
                house = House.objects.create(
                    name='Тестовый домик 1',
                    description='Тестовое описание 1',
                    holidays_multiplier=holiday_multiplier_test_value,
                )
            except ValidationError:
                continue
            else:
                house.delete()
                assert False, f"Создан домик с множителем {holiday_multiplier_test_value}, " \
                              f"при минимальной {Pricing.MIN_HOUSE_HOLIDAYS_MULTIPLIER}"

        # проверка, что можно создать домик с минимальной ценой
        try:
            house = House.objects.create(
                name='Тестовый домик 1',
                description='Тестовое описание 1',
                holidays_multiplier=Pricing.MIN_HOUSE_HOLIDAYS_MULTIPLIER,
            )
        except ValidationError:
            assert False, \
                f"Не удалось создать домик с множителем {Pricing.MIN_HOUSE_HOLIDAYS_MULTIPLIER}, " \
                f"при минимальной {Pricing.MIN_HOUSE_HOLIDAYS_MULTIPLIER}"


class HouseReservationModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создаём тестовую запись в БД
        # и сохраняем созданную запись в качестве переменной класса
        cls.house = House.objects.create(
            name='Тестовый домик',
            description='Тестовое описание',
        )
        cls.client = Client.objects.create(
            email="client1@email.com",
            first_name="Client1_first_name",
            last_name="Client1_second_name"
        )

        cls.now_in = now().replace(hour=16, minute=0, second=0, microsecond=0)
        cls.now_out = now().replace(hour=12, minute=0, second=0, microsecond=0)

        cls.default_reservation_arguments = {'house': cls.house, 'client': cls.client,
                                             'preferred_contact': 'none', 'comment': 'none'}

    def test_verbose_name(self):
        """verbose_name в полях совпадает с ожидаемым."""
        reservation = HouseReservation.objects.create(
            **HouseReservationModelTest.default_reservation_arguments,
            check_in_datetime=HouseReservationModelTest.now_in + timedelta(days=1),
            check_out_datetime=HouseReservationModelTest.now_out + timedelta(days=2),
        )

        field_verboses = {
            'house': "Домик",
            'client': "Клиент",
            'check_in_datetime': "Дата и время заезда",
            'check_out_datetime': "Дата и время выезда",
            "price": "Стоимость",
            'preferred_contact': "Предпочтительный способ связи",
            'comment': "Комментарий",
            'created_at': "Время создания бронирования",
            'updated_at': "Время последнего изменения бронирования",
        }

        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    reservation._meta.get_field(field).verbose_name, expected_value)

    def test_cant_reserve_past_dates(self):
        for check_in_delta, check_out_delta in [(-1, 0), (0, 1), (-1, 1), (-5, -4), (-5, 10), (-10, -8)]:
            try:
                HouseReservationModelTest.reservation = HouseReservation.objects.create(
                    **HouseReservationModelTest.default_reservation_arguments,
                    check_in_datetime=HouseReservationModelTest.now_in + timedelta(days=check_in_delta),
                    check_out_datetime=HouseReservationModelTest.now_out + timedelta(days=check_out_delta),
                )
            except ValidationError:
                pass
            else:
                assert False, f"Создано бронирование начинающееся через {check_in_delta} дней " \
                              f"И заканчивающееся через {check_out_delta} дней (test_cant_reserve_past_dates)"

    def test_correct_date_range(self):
        for check_in_delta, check_out_delta in [(2, 1), (5, 2), (10, 3)]:
            try:
                HouseReservation.objects.create(
                    **HouseReservationModelTest.default_reservation_arguments,
                    check_in_datetime=HouseReservationModelTest.now_in + timedelta(days=check_in_delta),
                    check_out_datetime=HouseReservationModelTest.now_out + timedelta(days=check_out_delta),
                )
            except ValidationError:
                continue
            else:
                assert False, f"Создано бронирование начинающееся через {check_in_delta} дней " \
                              f"И заканчивающееся через {check_out_delta} дней (test_correct_date_range)"

    # def test_exclude_reservations_overlapping(self):
    # TODO
    #     raise ZeroDivisionError

    # def test_price_generations(self):
    # TODO
    #     raise ZeroDivisionError
