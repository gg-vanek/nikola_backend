from django.conf import settings

from core.models import Pricing
from house_reservations_billing.models.constants import (
    EARLY_CHECK_IN_POSITION,
    NIGHT_POSITION,
    LATE_CHECK_OUT_POSITION,
    EXTRA_PERSONS_POSITION,
    PROMO_CODE_POSITION,
)

BILL_POSITION_IMAGE_PATH = {
    EARLY_CHECK_IN_POSITION: settings.MEDIA_ROOT + "/notifications/new_reservation/bill_position/early_check_in.png",
    NIGHT_POSITION: settings.MEDIA_ROOT + "/notifications/new_reservation/bill_position/night.png",
    LATE_CHECK_OUT_POSITION: settings.MEDIA_ROOT + "/notifications/new_reservation/bill_position/late_check_out.png",
    EXTRA_PERSONS_POSITION: settings.MEDIA_ROOT + "/notifications/new_reservation/bill_position/extra_persons.png",
    PROMO_CODE_POSITION: settings.MEDIA_ROOT + "/notifications/new_reservation/bill_position/promocode.png",
}

RESERVATION_TIME_IMAGE_PATH = {
    Pricing.ALLOWED_CHECK_IN_TIMES["earliest"]: settings.MEDIA_ROOT + "/notifications/new_reservation/timing/sun.png",
    Pricing.ALLOWED_CHECK_IN_TIMES["latest"]: settings.MEDIA_ROOT + "/notifications/new_reservation/timing/moon.png",
    Pricing.ALLOWED_CHECK_OUT_TIMES["earliest"]: settings.MEDIA_ROOT + "/notifications/new_reservation/timing/sun.png",
    Pricing.ALLOWED_CHECK_OUT_TIMES["latest"]: settings.MEDIA_ROOT + "/notifications/new_reservation/timing/moon.png",
}
