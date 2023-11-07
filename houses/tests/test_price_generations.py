from datetime import timedelta

from datetime import datetime as Datetime
from django.test import TestCase
from django.utils.timezone import now

from clients.models import Client
from events.models import Event
from houses.models import House, HouseReservation

from houses.services.price_calculators import calculate_reservation_receipt, Receipt, ReceiptPosition


class PriceGenerationTest(TestCase):
    client: Client
    house1: House
    house2: House
    house3: House

    saturday: Datetime
    default_check_in: Datetime
    early_check_in: Datetime

    default_check_out: Datetime
    late_check_out: Datetime

    default_reservation_arguments: dict

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создаём тестовую запись в БД
        # и сохраняем созданную запись в качестве переменной класса
        cls.client = Client.objects.create(
            email="client1@email.com",
            first_name="Client1_first_name",
            last_name="Client1_second_name"
        )

        cls.house1 = House.objects.create(
            name='Домик1',
            description='Тестовое описание',
            holidays_multiplier=1.5,
            base_price=5000,
        )
        cls.house2 = House.objects.create(
            name='Домик2',
            description='Тестовое описание',
            holidays_multiplier=1.7,
            base_price=7000,
        )
        cls.house3 = House.objects.create(
            name='Домик3',
            description='Тестовое описание',
            holidays_multiplier=2,
            base_price=10000,
            base_persons_amount=2,
            max_persons_amount=5,
            price_per_extra_person=3000,
        )

        # беру именно субботу, потому что когда руками высчитывал
        # стоимости первым днем в тестовом календарике поставил субботу
        cls.saturday = now() + timedelta(days=5 - now().weekday() + 7)
        # сегодня пн -> weekday = 0 -> saturday наступит через 5 - 0 + 7 = 12 дней
        # сегодня вт -> weekday = 1 -> saturday наступит через 5 - 1 + 7 = 11 дней
        # сегодня ср -> weekday = 2 -> saturday наступит через 5 - 2 + 7 = 10 дней
        # сегодня чт -> weekday = 3 -> saturday наступит через 5 - 3 + 7 = 9 дней
        # сегодня пт -> weekday = 4 -> saturday наступит через 5 - 4 + 7 = 8 дней
        # сегодня сб -> weekday = 5 -> saturday наступит через 5 - 5 + 7 = 7 дней
        # сегодня вс -> weekday = 6 -> saturday наступит через 5 - 6 + 7 = 6 дней

        cls.default_check_in = cls.saturday.replace(hour=16, minute=0, second=0, microsecond=0)
        cls.early_check_in = cls.saturday.replace(hour=13, minute=0, second=0, microsecond=0)

        cls.default_check_out = cls.saturday.replace(hour=12, minute=0, second=0, microsecond=0)
        cls.late_check_out = cls.saturday.replace(hour=15, minute=0, second=0, microsecond=0)

        cls.default_reservation_arguments = {'client': cls.client, 'preferred_contact': 'none', 'comment': 'none'}

    def test_price_calculation_on_reservation_create(self):
        cls = PriceGenerationTest
        event = Event.objects.create(
            name="Событие",
            multiplier=4,
            start_date=(cls.saturday + timedelta(days=12)).date(),
            end_date=(cls.saturday + timedelta(days=15)).date(),
        )
        for test_parameters in [
            {
                "reservation_parameters": {
                    "house": cls.house1,
                    "check_in_datetime": cls.default_check_in + timedelta(days=1),
                    "check_out_datetime": cls.default_check_out + timedelta(days=3),
                    "extra_persons_amount": 0,
                },
                "expected_price": 10_000,
            },
            {
                "reservation_parameters": {
                    "house": cls.house2,
                    "check_in_datetime": cls.early_check_in + timedelta(days=1),
                    "check_out_datetime": cls.default_check_out + timedelta(days=3),
                    "extra_persons_amount": 0,
                },
                "expected_price": 17_600,
            },
            {
                "reservation_parameters": {
                    "house": cls.house3,
                    "check_in_datetime": cls.default_check_in + timedelta(days=1),
                    "check_out_datetime": cls.late_check_out + timedelta(days=3),
                    "extra_persons_amount": 0,
                },
                "expected_price": 23_000,
            },
            {
                "reservation_parameters": {
                    "house": cls.house3,
                    "check_in_datetime": cls.early_check_in + timedelta(days=5),
                    "check_out_datetime": cls.late_check_out + timedelta(days=8),
                    "extra_persons_amount": 2,
                },
                "expected_price": 77_000,
            },
            {
                "reservation_parameters": {
                    "house": cls.house1,
                    "check_in_datetime": cls.early_check_in + timedelta(days=10),
                    "check_out_datetime": cls.late_check_out + timedelta(days=13),
                    "extra_persons_amount": 1,
                },
                "expected_price": 58_500,
            },
            {
                "reservation_parameters": {
                    "house": cls.house3,
                    "check_in_datetime": cls.default_check_in + timedelta(days=11),
                    "check_out_datetime": cls.late_check_out + timedelta(days=15),
                    "extra_persons_amount": 3,
                },
                "expected_price": 300_000,
            },
        ]:
            reservation = HouseReservation.objects.create(
                **cls.default_reservation_arguments,
                **test_parameters["reservation_parameters"],
            )

            self.assertEqual(reservation.price,
                             test_parameters["expected_price"])

            # reservation.delete() удалять бронирования не надо - они по замыслу не пересекаются
        event.delete()

    def test_receipt_generation_func(self):
        cls = PriceGenerationTest
        event = Event.objects.create(
            name="Событие",
            multiplier=4,
            start_date=(cls.saturday + timedelta(days=12)).date(),
            end_date=(cls.saturday + timedelta(days=15)).date(),
        )
        for test_parameters in [
            {
                "reservation_parameters": {
                    "house": cls.house1,
                    "check_in_datetime": cls.default_check_in + timedelta(days=1),
                    "check_out_datetime": cls.default_check_out + timedelta(days=3),
                    "extra_persons_amount": 0,
                },
                "expected_price": 10_000,
                "expected_receipt": Receipt(
                    nights=[
                        ReceiptPosition(
                            date=(cls.default_check_in + timedelta(days=2)).date(),
                            price=5_000
                        ),
                        ReceiptPosition(
                            date=(cls.default_check_in + timedelta(days=3)).date(),
                            price=5_000
                        ),
                    ]
                )
            },
            {
                "reservation_parameters": {
                    "house": cls.house2,
                    "check_in_datetime": cls.early_check_in + timedelta(days=1),
                    "check_out_datetime": cls.default_check_out + timedelta(days=3),
                    "extra_persons_amount": 0,
                },
                "expected_price": 17_600,
                "expected_receipt": Receipt(
                    extra_services=[
                        ReceiptPosition(
                            date=(cls.early_check_in + timedelta(days=1)).date(),
                            time=(cls.early_check_in + timedelta(days=1)).time(),
                            type="early_check_in",
                            price=3_600
                        )
                    ],
                    nights=[
                        ReceiptPosition(
                            date=(cls.default_check_in + timedelta(days=2)).date(),
                            price=7_000
                        ),
                        ReceiptPosition(
                            date=(cls.default_check_in + timedelta(days=3)).date(),
                            price=7_000
                        ),
                    ]
                )
            },
            {
                "reservation_parameters": {
                    "house": cls.house3,
                    "check_in_datetime": cls.default_check_in + timedelta(days=1),
                    "check_out_datetime": cls.late_check_out + timedelta(days=3),
                    "extra_persons_amount": 0,
                },
                "expected_price": 23_000,
                "expected_receipt": Receipt(
                    extra_services=[
                        ReceiptPosition(
                            date=(cls.late_check_out + timedelta(days=3)).date(),
                            time=(cls.late_check_out + timedelta(days=3)).time(),
                            type="late_check_out",
                            price=3_000
                        ),
                    ],
                    nights=[
                        ReceiptPosition(
                            date=(cls.default_check_in + timedelta(days=2)).date(),
                            price=10_000
                        ),
                        ReceiptPosition(
                            date=(cls.default_check_in + timedelta(days=3)).date(),
                            price=10_000
                        ),
                    ]
                )
            },
            {
                "reservation_parameters": {
                    "house": cls.house3,
                    "check_in_datetime": cls.early_check_in + timedelta(days=5),
                    "check_out_datetime": cls.late_check_out + timedelta(days=8),
                    "extra_persons_amount": 2,
                },
                "expected_price": 77_000,
                "expected_receipt": Receipt(
                    extra_services=[
                        ReceiptPosition(
                            date=(cls.early_check_in + timedelta(days=5)).date(),
                            time=(cls.early_check_in + timedelta(days=5)).time(),
                            type="early_check_in",
                            price=3_000
                        ),
                        ReceiptPosition(
                            date=(cls.late_check_out + timedelta(days=8)).date(),
                            time=(cls.late_check_out + timedelta(days=8)).time(),
                            type="late_check_out",
                            price=6_000
                        ),
                    ],
                    nights=[
                        ReceiptPosition(
                            date=(cls.default_check_in + timedelta(days=6)).date(),
                            price=16_000
                        ),
                        ReceiptPosition(
                            date=(cls.default_check_in + timedelta(days=7)).date(),
                            price=26_000
                        ),
                        ReceiptPosition(
                            date=(cls.default_check_in + timedelta(days=8)).date(),
                            price=26_000
                        ),
                    ]
                )
            },
            {
                "reservation_parameters": {
                    "house": cls.house1,
                    "check_in_datetime": cls.early_check_in + timedelta(days=10),
                    "check_out_datetime": cls.late_check_out + timedelta(days=13),
                    "extra_persons_amount": 1,
                },
                "expected_price": 58_500,
                "expected_receipt": Receipt(
                    extra_services=[
                        ReceiptPosition(
                            date=(cls.early_check_in + timedelta(days=10)).date(),
                            time=(cls.early_check_in + timedelta(days=10)).time(),
                            type="early_check_in",
                            price=1_500
                        ),
                        ReceiptPosition(
                            date=(cls.late_check_out + timedelta(days=13)).date(),
                            time=(cls.late_check_out + timedelta(days=13)).time(),
                            type="late_check_out",
                            price=6_000
                        ),
                    ],
                    nights=[
                        ReceiptPosition(
                            date=(cls.default_check_in + timedelta(days=11)).date(),
                            price=7_000
                        ),
                        ReceiptPosition(
                            date=(cls.default_check_in + timedelta(days=12)).date(),
                            price=22_000
                        ),
                        ReceiptPosition(
                            date=(cls.default_check_in + timedelta(days=13)).date(),
                            price=22_000
                        ),
                    ]
                )
            },
            {
                "reservation_parameters": {
                    "house": cls.house3,
                    "check_in_datetime": cls.default_check_in + timedelta(days=11),
                    "check_out_datetime": cls.late_check_out + timedelta(days=15),
                    "extra_persons_amount": 3,
                },
                "expected_price": 300_000,
                "expected_receipt": Receipt(
                    extra_services=[
                        ReceiptPosition(
                            date=(cls.late_check_out + timedelta(days=15)).date(),
                            time=(cls.late_check_out + timedelta(days=15)).time(),
                            type="late_check_out",
                            price=24_000
                        ),
                    ],
                    nights=[
                        ReceiptPosition(
                            date=(cls.default_check_in + timedelta(days=12)).date(),
                            price=49_000
                        ),
                        ReceiptPosition(
                            date=(cls.default_check_in + timedelta(days=13)).date(),
                            price=49_000
                        ),
                        ReceiptPosition(
                            date=(cls.default_check_in + timedelta(days=14)).date(),
                            price=89_000
                        ),
                        ReceiptPosition(
                            date=(cls.default_check_in + timedelta(days=15)).date(),
                            price=89_000
                        ),
                    ]
                )
            },
        ]:
            receipt = calculate_reservation_receipt(**test_parameters["reservation_parameters"])
            self.assertEqual(receipt.total, test_parameters["expected_price"])
            self.assertEqual(receipt,
                             test_parameters["expected_receipt"],
                             msg=f"\n{receipt}\n"
                                 f"---------\n"
                                 f"{test_parameters['expected_receipt']}")

            # reservation.delete() удалять бронирования не надо - они по замыслу не пересекаются
        event.delete()

    # def test_promos(self):
