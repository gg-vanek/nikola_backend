from datetime import timedelta

from datetime import datetime as Datetime
from django.core.exceptions import ModelValidationError
from django.test import TestCase
from django.utils.timezone import now

from clients.models import Client
from events.models import Event
from houses.models import House
from house_reservations.models import HouseReservation

from billing.services.price_calculators import light_calculate_reservation_price


class HouseReservationModelTest(TestCase):
    house: House
    client: Client
    default_reservation_arguments: dict

    today_default_check_in: Datetime
    today_early_check_in: Datetime

    today_default_check_out: Datetime
    today_late_check_out: Datetime

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создаём тестовую запись в БД
        # и сохраняем созданную запись в качестве переменной класса
        cls.house = House.objects.create(
            name='Домик',
            description='Тестовое описание',
            holidays_multiplier=1.5,
            base_price=7500,
            base_persons_amount=2,
            max_persons_amount=5,
            price_per_extra_person=2000,
        )
        cls.client = Client.objects.create(
            email="client1@email.com",
            first_name="Client1_first_name",
            last_name="Client1_second_name"
        )

        cls.today_default_check_in = now().replace(hour=16, minute=0, second=0, microsecond=0)
        cls.today_early_check_in = now().replace(hour=13, minute=0, second=0, microsecond=0)

        cls.today_default_check_out = now().replace(hour=12, minute=0, second=0, microsecond=0)
        cls.today_late_check_out = now().replace(hour=15, minute=0, second=0, microsecond=0)

        cls.default_reservation_arguments = {'house': cls.house, 'client': cls.client,
                                             'preferred_contact': 'none', 'comment': 'none'}

    def test_verbose_name(self):
        """verbose_name в полях совпадает с ожидаемым."""
        reservation = HouseReservation.objects.create(
            **HouseReservationModelTest.default_reservation_arguments,
            total_persons_amount=2,
            check_in_datetime=HouseReservationModelTest.today_default_check_in + timedelta(days=1),
            check_out_datetime=HouseReservationModelTest.today_default_check_out + timedelta(days=2),
        )

        field_verboses = {
            'house': "Домик",
            'client': "Клиент",
            'check_in_datetime': "Дата и время заезда",
            'check_out_datetime': "Дата и время выезда",
            "total_persons_amount": "Количество человек для проживания в домике",
            "price": "Стоимость",
            'preferred_contact': "Предпочтительный способ связи",
            'comment': "Комментарий",
            "cancelled": "Отменено?",
            'created_at': "Время создания бронирования",
            'updated_at': "Время последнего изменения бронирования",
        }

        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(reservation._meta.get_field(field).verbose_name, expected_value)

    def test_cant_reserve_past_dates(self):
        for check_in_delta, check_out_delta in [(-1, 0), (0, 1), (-1, 1), (-5, -4), (-5, 10), (-10, -8)]:
            with self.assertRaises(ModelValidationError,
                                   msg=f"Создано бронирование начинающееся через {check_in_delta} дней "
                                       f"И заканчивающееся через {check_out_delta} дней"):
                reservation = HouseReservation.objects.create(
                    **HouseReservationModelTest.default_reservation_arguments,
                    total_persons_amount=2,
                    check_in_datetime=HouseReservationModelTest.today_default_check_in
                                      + timedelta(days=check_in_delta),
                    check_out_datetime=HouseReservationModelTest.today_default_check_out
                                       + timedelta(days=check_out_delta),
                )
                reservation.delete()

        try:
            HouseReservation.objects.create(
                **HouseReservationModelTest.default_reservation_arguments,
                total_persons_amount=2,
                check_in_datetime=HouseReservationModelTest.today_default_check_in + timedelta(days=1),
                check_out_datetime=HouseReservationModelTest.today_default_check_out + timedelta(days=3),
            )
        except ModelValidationError:
            self.fail(msg=f"Не удалось создать бронирование начинающееся через {check_in_delta} дней "
                          f"И заканчивающееся через {check_out_delta} дней")

    def test_correct_date_range(self):
        for check_in_delta, check_out_delta in [(2, 1), (5, 2), (10, 3)]:
            with self.assertRaises(ModelValidationError,
                                   msg=f"Создано бронирование начинающееся через {check_in_delta} дней "
                                       f"И заканчивающееся через {check_out_delta} дней (test_correct_date_range)"):
                reservation = HouseReservation.objects.create(
                    **HouseReservationModelTest.default_reservation_arguments,
                    total_persons_amount=2,
                    check_in_datetime=HouseReservationModelTest.today_default_check_in + timedelta(days=check_in_delta),
                    check_out_datetime=HouseReservationModelTest.today_default_check_out + timedelta(
                        days=check_out_delta),
                )
                reservation.delete()

        try:
            HouseReservation.objects.create(
                **HouseReservationModelTest.default_reservation_arguments,
                total_persons_amount=2,
                check_in_datetime=HouseReservationModelTest.today_default_check_in + timedelta(days=1),
                check_out_datetime=HouseReservationModelTest.today_default_check_out + timedelta(days=3),
            )
        except ModelValidationError:
            self.fail(msg=f"Не удалось создать бронирование начинающееся через {check_in_delta} дней "
                          f"И заканчивающееся через {check_out_delta} дней")

    def test_exclude_reservations_overlapping(self):
        for test_parameters in \
                [
                    # Notation:
                    #  - . day with no reservation
                    #  - x day with reservation and default check_in/check_out time
                    #  - X day with reservation and not default check_in/check_out time
                    #  - first line describes first reservation, second line - second reservation

                    {
                        "reservation1": {
                            "check_in_datetime": HouseReservationModelTest.today_default_check_in + timedelta(days=1),
                            "check_out_datetime": HouseReservationModelTest.today_default_check_out + timedelta(days=2),
                        },
                        "reservation2": {
                            "check_in_datetime": HouseReservationModelTest.today_default_check_in + timedelta(days=1),
                            "check_out_datetime": HouseReservationModelTest.today_default_check_out + timedelta(days=3),
                        },
                        "test_description": "\n.xx."
                                            "\n.xxx\n",
                        "expected_result": "fail",
                    },
                    {
                        "reservation1": {
                            "check_in_datetime": HouseReservationModelTest.today_default_check_in + timedelta(days=1),
                            "check_out_datetime": HouseReservationModelTest.today_default_check_out + timedelta(days=3),
                        },
                        "reservation2": {
                            "check_in_datetime": HouseReservationModelTest.today_default_check_in + timedelta(days=1),
                            "check_out_datetime": HouseReservationModelTest.today_default_check_out + timedelta(days=2),
                        },
                        "test_description": "\n.xxx"
                                            "\n.xx.\n",
                        "expected_result": "fail",
                    },
                    {
                        "reservation1": {
                            "check_in_datetime": HouseReservationModelTest.today_default_check_in + timedelta(days=2),
                            "check_out_datetime": HouseReservationModelTest.today_default_check_out + timedelta(days=3),
                        },
                        "reservation2": {
                            "check_in_datetime": HouseReservationModelTest.today_default_check_in + timedelta(days=1),
                            "check_out_datetime": HouseReservationModelTest.today_default_check_out + timedelta(days=3),
                        },
                        "test_description": "\n..xx"
                                            "\n.xxx\n",
                        "expected_result": "fail",
                    },
                    {
                        "reservation1": {
                            "check_in_datetime": HouseReservationModelTest.today_default_check_in + timedelta(days=1),
                            "check_out_datetime": HouseReservationModelTest.today_default_check_out + timedelta(days=3),
                        },
                        "reservation2": {
                            "check_in_datetime": HouseReservationModelTest.today_default_check_in + timedelta(days=2),
                            "check_out_datetime": HouseReservationModelTest.today_default_check_out + timedelta(days=3),
                        },
                        "test_description": "\n.xxx"
                                            "\n..xx\n",
                        "expected_result": "fail",
                    },
                    {
                        "reservation1": {
                            "check_in_datetime": HouseReservationModelTest.today_default_check_in + timedelta(days=1),
                            "check_out_datetime": HouseReservationModelTest.today_default_check_out + timedelta(days=5),
                        },
                        "reservation2": {
                            "check_in_datetime": HouseReservationModelTest.today_default_check_in + timedelta(days=2),
                            "check_out_datetime": HouseReservationModelTest.today_default_check_out + timedelta(days=4),
                        },
                        "test_description": "\n.xxxxx"
                                            "\n..xxx.\n",
                        "expected_result": "fail",
                    },
                    {
                        "reservation1": {
                            "check_in_datetime": HouseReservationModelTest.today_default_check_in + timedelta(days=2),
                            "check_out_datetime": HouseReservationModelTest.today_default_check_out + timedelta(days=4),
                        },
                        "reservation2": {
                            "check_in_datetime": HouseReservationModelTest.today_default_check_in + timedelta(days=1),
                            "check_out_datetime": HouseReservationModelTest.today_default_check_out + timedelta(days=5),
                        },
                        "test_description": "\n..xxx."
                                            "\n.xxxxx\n",
                        "expected_result": "fail",
                    },
                    {
                        "reservation1": {
                            "check_in_datetime": HouseReservationModelTest.today_default_check_in + timedelta(days=1),
                            "check_out_datetime": HouseReservationModelTest.today_default_check_out + timedelta(days=3),
                        },
                        "reservation2": {
                            "check_in_datetime": HouseReservationModelTest.today_default_check_in + timedelta(days=1),
                            "check_out_datetime": HouseReservationModelTest.today_late_check_out + timedelta(days=3),
                        },
                        "test_description": "\n.xxx."
                                            "\n.xxx.\n",
                        "expected_result": "fail",
                    },
                    {
                        "reservation1": {
                            "check_in_datetime": HouseReservationModelTest.today_early_check_in + timedelta(days=1),
                            "check_out_datetime": HouseReservationModelTest.today_default_check_out + timedelta(days=4),
                        },
                        "reservation2": {
                            "check_in_datetime": HouseReservationModelTest.today_default_check_in + timedelta(days=2),
                            "check_out_datetime": HouseReservationModelTest.today_late_check_out + timedelta(days=5),
                        },
                        "test_description": "\n.xxxx.."
                                            "\n..xxxx.\n",
                        "expected_result": "fail",
                    },
                    {
                        "reservation1": {
                            "check_in_datetime": HouseReservationModelTest.today_early_check_in + timedelta(days=2),
                            "check_out_datetime": HouseReservationModelTest.today_default_check_out + timedelta(days=5),
                        },
                        "reservation2": {
                            "check_in_datetime": HouseReservationModelTest.today_default_check_in + timedelta(days=1),
                            "check_out_datetime": HouseReservationModelTest.today_late_check_out + timedelta(days=4),
                        },
                        "test_description": "\n..xxxx."
                                            "\n.xxxx..\n",
                        "expected_result": "fail",
                    },
                    {
                        "reservation1": {
                            "check_in_datetime": HouseReservationModelTest.today_default_check_in + timedelta(days=1),
                            "check_out_datetime": HouseReservationModelTest.today_late_check_out + timedelta(days=3),
                        },
                        "reservation2": {
                            "check_in_datetime": HouseReservationModelTest.today_early_check_in + timedelta(days=3),
                            "check_out_datetime": HouseReservationModelTest.today_default_check_out + timedelta(days=5),
                        },
                        "test_description": "\n.xxX.."
                                            "\n...Xxx\n",
                        "expected_result": "fail",
                    },
                    {
                        "reservation1": {
                            "check_in_datetime": HouseReservationModelTest.today_early_check_in + timedelta(days=3),
                            "check_out_datetime": HouseReservationModelTest.today_default_check_out + timedelta(days=5),
                        },
                        "reservation2": {
                            "check_in_datetime": HouseReservationModelTest.today_default_check_in + timedelta(days=1),
                            "check_out_datetime": HouseReservationModelTest.today_late_check_out + timedelta(days=3),
                        },
                        "test_description": "\n...Xxx"
                                            "\n.xxX..\n",
                        "expected_result": "fail",
                    },
                    {
                        "reservation1": {
                            "check_in_datetime": HouseReservationModelTest.today_early_check_in + timedelta(days=3),
                            "check_out_datetime": HouseReservationModelTest.today_default_check_out + timedelta(days=5),
                        },
                        "reservation2": {
                            "check_in_datetime": HouseReservationModelTest.today_default_check_in + timedelta(days=1),
                            "check_out_datetime": HouseReservationModelTest.today_default_check_out + timedelta(days=3),
                        },
                        "test_description": "\n...Xxx"
                                            "\n.xxx..\n",
                        "expected_result": "pass",
                    },
                    {
                        "reservation1": {
                            "check_in_datetime": HouseReservationModelTest.today_default_check_in + timedelta(days=1),
                            "check_out_datetime": HouseReservationModelTest.today_default_check_out + timedelta(days=3),
                        },
                        "reservation2": {
                            "check_in_datetime": HouseReservationModelTest.today_early_check_in + timedelta(days=3),
                            "check_out_datetime": HouseReservationModelTest.today_default_check_out + timedelta(days=5),
                        },
                        "test_description": "\n.xxx.."
                                            "\n...Xxx\n",
                        "expected_result": "pass",
                    },
                    {
                        "reservation1": {
                            "check_in_datetime": HouseReservationModelTest.today_default_check_in + timedelta(days=3),
                            "check_out_datetime": HouseReservationModelTest.today_default_check_out + timedelta(days=5),
                        },
                        "reservation2": {
                            "check_in_datetime": HouseReservationModelTest.today_default_check_in + timedelta(days=1),
                            "check_out_datetime": HouseReservationModelTest.today_late_check_out + timedelta(days=3),
                        },
                        "test_description": "\n...xxx"
                                            "\n.xxX..\n",
                        "expected_result": "pass",
                    },
                    {
                        "reservation1": {
                            "check_in_datetime": HouseReservationModelTest.today_default_check_in + timedelta(days=1),
                            "check_out_datetime": HouseReservationModelTest.today_late_check_out + timedelta(days=3),
                        },
                        "reservation2": {
                            "check_in_datetime": HouseReservationModelTest.today_default_check_in + timedelta(days=3),
                            "check_out_datetime": HouseReservationModelTest.today_default_check_out + timedelta(days=5),
                        },
                        "test_description": "\n.xxX.."
                                            "\n...xxx\n",
                        "expected_result": "pass",
                    },
                    {
                        "reservation1": {
                            "check_in_datetime": HouseReservationModelTest.today_default_check_in + timedelta(days=1),
                            "check_out_datetime": HouseReservationModelTest.today_default_check_out + timedelta(days=3),
                        },
                        "reservation2": {
                            "check_in_datetime": HouseReservationModelTest.today_default_check_in + timedelta(days=3),
                            "check_out_datetime": HouseReservationModelTest.today_default_check_out + timedelta(days=5),
                        },
                        "test_description": "\n.xxx.."
                                            "\n...xxx\n",
                        "expected_result": "pass",
                    },
                    {
                        "reservation1": {
                            "check_in_datetime": HouseReservationModelTest.today_default_check_in + timedelta(days=3),
                            "check_out_datetime": HouseReservationModelTest.today_default_check_out + timedelta(days=5),
                        },
                        "reservation2": {
                            "check_in_datetime": HouseReservationModelTest.today_default_check_in + timedelta(days=1),
                            "check_out_datetime": HouseReservationModelTest.today_default_check_out + timedelta(days=3),
                        },
                        "test_description": "\n...xxx"
                                            "\n.xxx..\n",
                        "expected_result": "pass",
                    },
                    {
                        "reservation1": {
                            "check_in_datetime": HouseReservationModelTest.today_default_check_in + timedelta(days=4),
                            "check_out_datetime": HouseReservationModelTest.today_default_check_out + timedelta(days=6),
                        },
                        "reservation2": {
                            "check_in_datetime": HouseReservationModelTest.today_default_check_in + timedelta(days=1),
                            "check_out_datetime": HouseReservationModelTest.today_default_check_out + timedelta(days=3),
                        },
                        "test_description": "\n....xxx"
                                            "\n.xxx...\n",
                        "expected_result": "pass",
                    },
                    {
                        "reservation1": {
                            "check_in_datetime": HouseReservationModelTest.today_default_check_in + timedelta(days=1),
                            "check_out_datetime": HouseReservationModelTest.today_default_check_out + timedelta(days=3),
                        },
                        "reservation2": {
                            "check_in_datetime": HouseReservationModelTest.today_default_check_in + timedelta(days=4),
                            "check_out_datetime": HouseReservationModelTest.today_default_check_out + timedelta(days=6),
                        },
                        "test_description": "\n.xxx..."
                                            "\n....xxx\n",
                        "expected_result": "pass",
                    },
                ]:

            reservation1 = HouseReservation.objects.create(
                **HouseReservationModelTest.default_reservation_arguments,
                total_persons_amount=2,
                **test_parameters["reservation1"],
            )
            if test_parameters["expected_result"] == "fail":
                with self.assertRaises(ModelValidationError,
                                       msg=f"Создана пара бронирований {test_parameters['test_description']}"):
                    reservation2 = HouseReservation.objects.create(
                        **HouseReservationModelTest.default_reservation_arguments,
                        total_persons_amount=2,
                        **test_parameters["reservation2"],
                    )
                    reservation2.delete()
            elif test_parameters["expected_result"] == "pass":
                try:
                    reservation2 = HouseReservation.objects.create(
                        **HouseReservationModelTest.default_reservation_arguments,
                        total_persons_amount=2,
                        **test_parameters["reservation2"],
                    )
                    reservation2.delete()
                except ModelValidationError:
                    self.fail(msg=f"Не удалось создать пару бронирований {test_parameters['test_description']}")
            else:
                raise ValueError(
                    f'Unexpected value of test_parameters["expected_result"] = {test_parameters["expected_result"]}')

            reservation1.delete()

    def test_cancel_reservation(self):
        # ниже огромное количество дублированного кода из функции test_exclude_reservations_overlapping
        for test_parameters in \
                [
                    # Notation:
                    #  - . day with no reservation
                    #  - x day with reservation and default check_in/check_out time
                    #  - X day with reservation and not default check_in/check_out time
                    #  - first line describes first reservation, second line - second reservation

                    {
                        "reservation1": {
                            "check_in_datetime": HouseReservationModelTest.today_default_check_in + timedelta(days=1),
                            "check_out_datetime": HouseReservationModelTest.today_default_check_out + timedelta(days=2),
                        },
                        "reservation2": {
                            "check_in_datetime": HouseReservationModelTest.today_default_check_in + timedelta(days=1),
                            "check_out_datetime": HouseReservationModelTest.today_default_check_out + timedelta(days=3),
                        },
                        "test_description": "\n.xx."
                                            "\n.xxx\n",
                        "expected_result": "fail",
                    },
                    {
                        "reservation1": {
                            "check_in_datetime": HouseReservationModelTest.today_default_check_in + timedelta(days=1),
                            "check_out_datetime": HouseReservationModelTest.today_default_check_out + timedelta(days=3),
                        },
                        "reservation2": {
                            "check_in_datetime": HouseReservationModelTest.today_default_check_in + timedelta(days=1),
                            "check_out_datetime": HouseReservationModelTest.today_default_check_out + timedelta(days=2),
                        },
                        "test_description": "\n.xxx"
                                            "\n.xx.\n",
                        "expected_result": "fail",
                    },
                    {
                        "reservation1": {
                            "check_in_datetime": HouseReservationModelTest.today_default_check_in + timedelta(days=2),
                            "check_out_datetime": HouseReservationModelTest.today_default_check_out + timedelta(days=3),
                        },
                        "reservation2": {
                            "check_in_datetime": HouseReservationModelTest.today_default_check_in + timedelta(days=1),
                            "check_out_datetime": HouseReservationModelTest.today_default_check_out + timedelta(days=3),
                        },
                        "test_description": "\n..xx"
                                            "\n.xxx\n",
                        "expected_result": "fail",
                    },
                    {
                        "reservation1": {
                            "check_in_datetime": HouseReservationModelTest.today_default_check_in + timedelta(days=1),
                            "check_out_datetime": HouseReservationModelTest.today_default_check_out + timedelta(days=3),
                        },
                        "reservation2": {
                            "check_in_datetime": HouseReservationModelTest.today_default_check_in + timedelta(days=2),
                            "check_out_datetime": HouseReservationModelTest.today_default_check_out + timedelta(days=3),
                        },
                        "test_description": "\n.xxx"
                                            "\n..xx\n",
                        "expected_result": "fail",
                    },
                    {
                        "reservation1": {
                            "check_in_datetime": HouseReservationModelTest.today_default_check_in + timedelta(days=1),
                            "check_out_datetime": HouseReservationModelTest.today_default_check_out + timedelta(days=5),
                        },
                        "reservation2": {
                            "check_in_datetime": HouseReservationModelTest.today_default_check_in + timedelta(days=2),
                            "check_out_datetime": HouseReservationModelTest.today_default_check_out + timedelta(days=4),
                        },
                        "test_description": "\n.xxxxx"
                                            "\n..xxx.\n",
                        "expected_result": "fail",
                    },
                    {
                        "reservation1": {
                            "check_in_datetime": HouseReservationModelTest.today_default_check_in + timedelta(days=2),
                            "check_out_datetime": HouseReservationModelTest.today_default_check_out + timedelta(days=4),
                        },
                        "reservation2": {
                            "check_in_datetime": HouseReservationModelTest.today_default_check_in + timedelta(days=1),
                            "check_out_datetime": HouseReservationModelTest.today_default_check_out + timedelta(days=5),
                        },
                        "test_description": "\n..xxx."
                                            "\n.xxxxx\n",
                        "expected_result": "fail",
                    },
                    {
                        "reservation1": {
                            "check_in_datetime": HouseReservationModelTest.today_default_check_in + timedelta(days=1),
                            "check_out_datetime": HouseReservationModelTest.today_default_check_out + timedelta(days=3),
                        },
                        "reservation2": {
                            "check_in_datetime": HouseReservationModelTest.today_default_check_in + timedelta(days=1),
                            "check_out_datetime": HouseReservationModelTest.today_late_check_out + timedelta(days=3),
                        },
                        "test_description": "\n.xxx."
                                            "\n.xxx.\n",
                        "expected_result": "fail",
                    },
                    {
                        "reservation1": {
                            "check_in_datetime": HouseReservationModelTest.today_early_check_in + timedelta(days=1),
                            "check_out_datetime": HouseReservationModelTest.today_default_check_out + timedelta(days=4),
                        },
                        "reservation2": {
                            "check_in_datetime": HouseReservationModelTest.today_default_check_in + timedelta(days=2),
                            "check_out_datetime": HouseReservationModelTest.today_late_check_out + timedelta(days=5),
                        },
                        "test_description": "\n.xxxx.."
                                            "\n..xxxx.\n",
                        "expected_result": "fail",
                    },
                    {
                        "reservation1": {
                            "check_in_datetime": HouseReservationModelTest.today_early_check_in + timedelta(days=2),
                            "check_out_datetime": HouseReservationModelTest.today_default_check_out + timedelta(days=5),
                        },
                        "reservation2": {
                            "check_in_datetime": HouseReservationModelTest.today_default_check_in + timedelta(days=1),
                            "check_out_datetime": HouseReservationModelTest.today_late_check_out + timedelta(days=4),
                        },
                        "test_description": "\n..xxxx."
                                            "\n.xxxx..\n",
                        "expected_result": "fail",
                    },
                    {
                        "reservation1": {
                            "check_in_datetime": HouseReservationModelTest.today_default_check_in + timedelta(days=1),
                            "check_out_datetime": HouseReservationModelTest.today_late_check_out + timedelta(days=3),
                        },
                        "reservation2": {
                            "check_in_datetime": HouseReservationModelTest.today_early_check_in + timedelta(days=3),
                            "check_out_datetime": HouseReservationModelTest.today_default_check_out + timedelta(days=5),
                        },
                        "test_description": "\n.xxX.."
                                            "\n...Xxx\n",
                        "expected_result": "fail",
                    },
                    {
                        "reservation1": {
                            "check_in_datetime": HouseReservationModelTest.today_early_check_in + timedelta(days=3),
                            "check_out_datetime": HouseReservationModelTest.today_default_check_out + timedelta(days=5),
                        },
                        "reservation2": {
                            "check_in_datetime": HouseReservationModelTest.today_default_check_in + timedelta(days=1),
                            "check_out_datetime": HouseReservationModelTest.today_late_check_out + timedelta(days=3),
                        },
                        "test_description": "\n...Xxx"
                                            "\n.xxX..\n",
                        "expected_result": "fail",
                    },
                ]:
            reservation1 = HouseReservation.objects.create(
                **HouseReservationModelTest.default_reservation_arguments,
                total_persons_amount=2,
                **test_parameters["reservation1"],
                cancelled=True,
            )

            try:
                reservation2 = HouseReservation.objects.create(
                    **HouseReservationModelTest.default_reservation_arguments,
                    total_persons_amount=2,
                    **test_parameters["reservation2"],
                )
                reservation2.delete()
            except ModelValidationError:
                self.fail(msg=f"Не удалось создать пару бронирований {test_parameters['test_description']}, "
                              f"при условии что первое отменили")

            reservation1.delete()

    def test_max_persons(self):
        for test_parameters in [
            {
                "expected_result": "fail",
                "total_persons_amount": 1,
            },
            {
                "expected_result": "pass",
                "total_persons_amount": 2,
            },
            {
                "expected_result": "pass",
                "total_persons_amount": 3,
            },
            {
                "expected_result": "pass",
                "total_persons_amount": 4,
            },
            {
                "expected_result": "pass",
                "total_persons_amount": 5,
            },
            {
                "expected_result": "fail",
                "total_persons_amount": 6,
            },
            {
                "expected_result": "fail",
                "total_persons_amount": 7,
            },
        ]:
            if test_parameters["expected_result"] == "fail":
                with self.assertRaises(
                        ModelValidationError,
                        msg=f"Создалось бронирование\n"
                            f"Базовое количество человек: {HouseReservationModelTest.house.base_persons_amount}\n"
                            f"Дополнительно количество человек: {test_parameters['total_persons_amount']}\n"
                            f"Максимальное количество человек: {HouseReservationModelTest.house.max_persons_amount}"):
                    HouseReservation.objects.create(
                        **HouseReservationModelTest.default_reservation_arguments,
                        check_in_datetime=HouseReservationModelTest.today_default_check_in + timedelta(days=1),
                        check_out_datetime=HouseReservationModelTest.today_default_check_out + timedelta(days=3),
                        total_persons_amount=test_parameters["total_persons_amount"]
                    )
            elif test_parameters["expected_result"] == "pass":
                try:
                    reservation = HouseReservation.objects.create(
                        **HouseReservationModelTest.default_reservation_arguments,
                        check_in_datetime=HouseReservationModelTest.today_default_check_in + timedelta(days=1),
                        check_out_datetime=HouseReservationModelTest.today_default_check_out + timedelta(days=3),
                        total_persons_amount=test_parameters["total_persons_amount"]
                    )
                    reservation.delete()
                except ModelValidationError:
                    self.fail(msg=f"Не удалось создать бронирование\n"
                                  f"Базовое количество человек: {HouseReservationModelTest.house.base_persons_amount}\n"
                                  f"Дополнительно количество человек: {test_parameters['total_persons_amount']}\n"
                                  f"Максимальное количество человек: "
                                  f"{HouseReservationModelTest.house.max_persons_amount}")

    def test_price_generations(self):
        event = Event.objects.create(
            name="Событие",
            multiplier=1.5,
            start_date=HouseReservationModelTest.today_default_check_in + timedelta(days=2),
            end_date=HouseReservationModelTest.today_default_check_in + timedelta(days=4),
        )
        for test_params in [
            {
                'check_in_datetime': HouseReservationModelTest.today_default_check_in + timedelta(days=1),
                'check_out_datetime': HouseReservationModelTest.today_default_check_out + timedelta(days=5),
                'total_persons_amount': 4,
            },
            {
                'check_in_datetime': HouseReservationModelTest.today_early_check_in + timedelta(days=3),
                'check_out_datetime': HouseReservationModelTest.today_default_check_out + timedelta(days=7),
                'total_persons_amount': 5,
            },
            {
                'check_in_datetime': HouseReservationModelTest.today_default_check_in + timedelta(days=1),
                'check_out_datetime': HouseReservationModelTest.today_late_check_out + timedelta(days=9),
                'total_persons_amount': 3,
            },
            {
                'check_in_datetime': HouseReservationModelTest.today_early_check_in + timedelta(days=2),
                'check_out_datetime': HouseReservationModelTest.today_late_check_out + timedelta(days=4),
                'total_persons_amount': 2,
            },
        ]:
            reservation = HouseReservation.objects.create(
                **HouseReservationModelTest.default_reservation_arguments,
                **test_params,
            )
            self.assertEqual(reservation.price,
                             light_calculate_reservation_price(house=HouseReservationModelTest.house,
                                                               **test_params))
            reservation.delete()
        event.delete()
