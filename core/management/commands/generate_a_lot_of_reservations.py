import random

from datetime import timedelta, datetime as Datetime

from django.core.management.base import BaseCommand
from django.utils.timezone import now

from clients.models import Client
from core.models import Pricing
from houses.models import House, HouseReservation


class Command(BaseCommand):
    """ Django command to pause execution until database is available"""

    def handle(self, *args, **kwargs):
        house_id = None
        client_id = None
        self.stdout.write('Generating house reservations ...')

        if house_id is None:
            house = House.objects.create(
                name=f"Домик {now()}",
                description="Описание",
                base_price=random.randint(50, 300) * 100,
                holidays_multiplier=random.uniform(1, 4),
                base_persons_amount=random.choice([1,2,3,4]),
                max_persons_amount=random.choice([5,6]),
                price_per_extra_person=random.randint(1, 50) * 100,
            )
        else:
            house = House.objects.get(id=house_id)

        if client_id is None:
            client = Client.objects.create(
                email=f"{Datetime.strftime(now(), '%d.%m.%Y.%H.%M.%S')}@mail.ru",
                first_name=f"{Datetime.strftime(now(), 'имечко %d-%m-%Y')}",
                last_name=f"{Datetime.strftime(now(), 'фамилия %H:%M:%S')}",
            )
        else:
            client = Client.objects.get(id=house_id)

        start = (now() + timedelta(days=3)).date()
        end = (now() + timedelta(days=5000)).date()
        counter = 0

        while start < end:
            HouseReservation.objects.create(
                client=client,
                house=house,
                check_in_datetime=Datetime.combine(start,
                                                   Pricing.ALLOWED_CHECK_IN_TIMES["default"]),
                check_out_datetime=Datetime.combine(start + timedelta(days=1),
                                                    Pricing.ALLOWED_CHECK_OUT_TIMES["default"]),
                extra_persons_amount=0,
                preferred_contact='a',
                comment='a',
            )
            start += timedelta(days=random.choice([1]))
            counter += 1

        self.stdout.write(f'Successfully Generated {counter} house reservations ...')
