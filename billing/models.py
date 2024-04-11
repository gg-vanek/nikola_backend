from datetime import timedelta

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.timezone import now

from billing.json_mappers import ChronologicalPositionsEncoder, ChronologicalPositionsDecoder, \
    NonChronologicalPositionsEncoder, NonChronologicalPositionsDecoder
from billing.services.price_calculators import calculate_house_price_by_day
from billing.text_helpers import *
from core.models import Pricing


class HouseReservationPromoCode(models.Model):
    FIXED_VALUE_DISCOUNT = "FIXED"
    PERCENTAGE_DISCOUNT = "PERCENTAGE"
    DISCOUNT_TYPE_CHOICES = {
        FIXED_VALUE_DISCOUNT: "Скидка на фиксированную сумму",
        PERCENTAGE_DISCOUNT: "Скидка на процент от чека"
    }
    discount_type_to_applying_function = {
        FIXED_VALUE_DISCOUNT: (lambda self, x: x - self.discount_value),
        PERCENTAGE_DISCOUNT: (lambda self, x: round(x * (100 - self.discount_value) / 100, -2)),
    }

    code = models.CharField(max_length=255, verbose_name="Промокод", unique=True)
    enabled = models.BooleanField(default=True)

    discount_type = models.CharField(max_length=15, choices=DISCOUNT_TYPE_CHOICES)
    discount_value = models.IntegerField()

    client = models.ForeignKey("clients.Client", default=None, null=True, blank=True, on_delete=models.CASCADE)
    max_use_times = models.IntegerField(default=1)
    minimal_bill_value = models.IntegerField(default=0)

    issuance_datetime = models.DateTimeField(default=None, null=True, blank=True)
    expiration_datetime = models.DateTimeField(default=None, null=True, blank=True)

    def apply(self, value: int, client, bill_id) -> int:
        self.check_availability(value, client, bill_id)
        return max(self.discount_type_to_applying_function[self.discount_type](self, value), 100)

    def check_availability(self, value, client, bill_id):
        # Check dates
        if self.issuance_datetime and now() < self.issuance_datetime:
            raise ValidationError(
                f"Промокод можно будет активировать с {self.issuance_datetime.strftime('%d-%m-%Y %H:%M')}")
        if self.expiration_datetime and now() > self.expiration_datetime:
            raise ValidationError(f"Промокод истек {self.expiration_datetime.strftime('%d-%m-%Y %H:%M')}")

        # Check client
        if self.client and client:  # когда происходит запрос цены бронирования информация приходит без клиента
            if self.client != client:
                raise ValidationError(f"Промокод принадлежит другому пользователю (идентификация по email)")

        # Check usages count
        if bill_id and self.bills.filter(id=bill_id):  # если чек уже сохранен в бд с этим промокодом
            pass
        elif self.bills.count() >= self.max_use_times:
            raise ValidationError('Промокод уже был использован максимальное количество раз')

        # Check bill value
        if value < self.minimal_bill_value:
            raise ValidationError(f'Промокод доступен при сумме в чеке от {self.minimal_bill_value}')

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def clean(self):
        if self.discount_type == self.PERCENTAGE_DISCOUNT:
            if not (0 <= self.discount_value <= 100):
                raise ValidationError('Промокод с типом "PERCENTAGE_DISCOUNT" '
                                      'должен иметь значение в промежутке от 0 до 100')

        if self.issuance_datetime and self.expiration_datetime:
            if self.issuance_datetime >= self.expiration_datetime:
                raise ValidationError(f'Некорректные даты действия промокода. '
                                      f'не выполнено self.issuance_datetime < self.expiration_datetime: '
                                      f'({self.issuance_datetime.strftime("%d-%m-%Y %H:%M")} '
                                      f'< {self.expiration_datetime.strftime("%d-%m-%Y %H:%M")})')

    def __str__(self):
        s = f"{self.code}: -{self.discount_value}"
        if self.discount_type == self.FIXED_VALUE_DISCOUNT:
            s += " руб."
        elif self.discount_type == self.PERCENTAGE_DISCOUNT:
            s += "%"
        else:
            s += " (!!!ПРОМОКОД С НЕКОРРЕКТНЫМ ТИПОМ!!!)"
        return s


class HouseReservationBill(models.Model):
    reservation = models.OneToOneField("house_reservations.HouseReservation",
                                       verbose_name="Счет на оплату бронирования домика",
                                       on_delete=models.CASCADE,
                                       null=True, blank=True, related_name='bill')

    total = models.IntegerField("Итоговая стоимость", validators=[MinValueValidator(100)])

    chronological_positions = models.JSONField(
        verbose_name="Хронологически упорядоченные позиции",
        default=dict, blank=True,
        encoder=ChronologicalPositionsEncoder,
        decoder=ChronologicalPositionsDecoder,
    )
    non_chronological_positions = models.JSONField(
        verbose_name="Хронологически неупорядоченные позиции",
        default=dict, blank=True,
        encoder=NonChronologicalPositionsEncoder,
        decoder=NonChronologicalPositionsDecoder,
    )

    promo_code = models.ForeignKey(
        verbose_name="Промокод",
        to="HouseReservationPromoCode", on_delete=models.SET_NULL, related_name='bills',
        default=None, null=True, blank=True,
    )

    paid = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Счет на оплату бронирования домика"
        verbose_name_plural = 'Счета на оплату бронирования домиков'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def calculate_value(self):
        house = self.reservation.house

        check_in_date = self.reservation.check_in_datetime.date()
        check_in_time = self.reservation.check_in_datetime.time()

        check_out_date = self.reservation.check_out_datetime.date()
        check_out_time = self.reservation.check_out_datetime.time()

        non_chronological_positions = []
        chronological_positions = []

        # NOTE: ночь идет перед днем
        # иными словами множитель выходного дня применяется к ночам пт-сб и сб-вс, но не к вс-пн
        date = check_in_date + timedelta(days=1)
        while date <= check_out_date:
            chronological_positions.append({
                "type": NIGHT_POSITION,
                "start_date": date - timedelta(days=1),
                "end_date": date,
                "price": calculate_house_price_by_day(house, date),
                "description": night_description(date - timedelta(days=1), date)
            })
            date = date + timedelta(days=1)

        # увеличение стоимости за ранний въезд и поздний выезд
        early_check_in = {
            "type": EARLY_CHECK_IN_POSITION,
            "time": check_in_time,
            "date": check_in_date,
            "price": Pricing.ALLOWED_CHECK_IN_TIMES.get(check_in_time, 0) *
                     calculate_house_price_by_day(house, check_in_date),
            "description": early_check_in_description(check_in_date, check_in_time)
        }
        if early_check_in["price"] != 0:
            chronological_positions.insert(0, early_check_in)

        late_check_out = {
            'type': LATE_CHECK_OUT_POSITION,
            "time": check_out_time,
            "date": check_out_date,
            "price": Pricing.ALLOWED_CHECK_OUT_TIMES.get(check_out_time, 0) *
                     calculate_house_price_by_day(house, check_out_date),
            "description": late_check_out_description(check_out_date, check_out_time)
        }
        if late_check_out["price"] != 0:
            chronological_positions.append(late_check_out)

        # увеличение стоимости за дополнительных людей
        extra_persons_amount = max(0, self.reservation.total_persons_amount - house.base_persons_amount)
        price_per_extra_person = house.price_per_extra_person
        nights_amount = (check_out_date - check_in_date).days

        if extra_persons_amount > 0:
            non_chronological_positions.append(
                {
                    "type": EXTRA_PERSONS_POSITION,
                    "extra_persons_amount": extra_persons_amount,
                    "price_per_extra_person": price_per_extra_person,
                    "nights_amount": nights_amount,
                    "price": extra_persons_amount * price_per_extra_person * nights_amount,
                    "description": f"{extra_persons_amount} доп. гостей х {nights_amount} ночей",
                }
            )

        if self.promo_code:
            old_price = sum(
                [ch_p["price"] for ch_p in chronological_positions] +
                [g_p["price"] for g_p in non_chronological_positions]
            )
            new_price = self.promo_code.apply(old_price, self.reservation.client, self.pk)
            discount = new_price - old_price

            non_chronological_positions.append(
                {
                    "type": PROMO_CODE_POSITION,
                    "promo_code": self.promo_code.code,
                    "price": discount,
                    "description": str(self.promo_code),
                }
            )

        self.chronological_positions = chronological_positions
        self.non_chronological_positions = non_chronological_positions

        self.total = sum(
            [ch_p["price"] for ch_p in chronological_positions] + [g_p["price"] for g_p in non_chronological_positions])

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def clean(self):
        self.calculate_value()

        # TODO Validate sum

    def __str__(self):
        return f"Счет на оплату бронирования ({self.reservation.id})"
