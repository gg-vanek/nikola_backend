import random
import time
from datetime import timedelta, datetime as Datetime

from django.core.management.base import BaseCommand
from django.utils.timezone import now

from clients.models import Client
from core.models import Pricing
from houses.models import House, HouseReservation


class Command(BaseCommand):
    """ Django command to pause execution until database is available"""

    def handle(self, *args, **kwargs):
        self.stdout.write(f'Deleting house reservations ...')
        HouseReservation.objects.all().delete()
        self.stdout.write(f'Successfully deleted house reservations ...')
