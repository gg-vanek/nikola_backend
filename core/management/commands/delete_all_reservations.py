from django.core.management.base import BaseCommand

from house_reservations.models import HouseReservation


class Command(BaseCommand):
    """ Django command to pause execution until database is available"""

    def handle(self, *args, **kwargs):
        self.stdout.write('Deleting house reservations ...')
        HouseReservation.objects.all().delete()
        self.stdout.write('Successfully deleted house reservations ...')
