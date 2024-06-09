import logging

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models

from core.models import Pricing
from houses.filepath_generators import generate_house_picture_filename, generate_house_feature_icon_filename

logger = logging.getLogger(__name__)


class House(models.Model):
    name = models.CharField("Название домика", max_length=255, unique=True)

    description = models.TextField("Описание домика")
    features = models.ManyToManyField("HouseFeature", verbose_name="Плюшки", related_name='houses')

    base_price = models.IntegerField(
        "Базовая цена",
        default=10000,
        validators=[
            MinValueValidator(Pricing.MIN_HOUSE_BASE_PRICE,
                              message=f"Базовая цена домика должна быть не меньше, "
                                      f"чем {Pricing.MIN_HOUSE_BASE_PRICE}"), ])
    holidays_multiplier = models.FloatField(
        "Множитель в выходные и праздники",
        default=2,
        validators=[
            MinValueValidator(Pricing.MIN_HOUSE_HOLIDAYS_MULTIPLIER,
                              message=f"Множитель в выходные дни должен быть не меньше, "
                                      f"чем {Pricing.MIN_HOUSE_HOLIDAYS_MULTIPLIER}"),
        ])

    base_persons_amount = models.IntegerField("Базовое количество человек для проживания в домике", default=2)
    max_persons_amount = models.IntegerField("Максимальное количество человек для проживания в домике", default=3)
    price_per_extra_person = models.IntegerField("Цена за дополнительного человека", default=2000)

    created_at = models.DateTimeField("Время создания домика", auto_now_add=True)
    updated_at = models.DateTimeField("Время последнего изменения домика", auto_now=True)

    class Meta:
        verbose_name = "Домик"
        verbose_name_plural = 'Домики'

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def clean(self):
        if self.max_persons_amount < self.base_persons_amount:
            raise ValidationError("Max persons amount must be greater than or equal to base persons amount")

    def __str__(self):
        return f"({self.id}) {self.name}"


class HousePicture(models.Model):
    house = models.ForeignKey(House, verbose_name="Домик",
                              on_delete=models.SET_NULL,
                              null=True, related_name='pictures')
    picture = models.ImageField("Путь до файла с изображением",
                                upload_to=generate_house_picture_filename)

    class Meta:
        verbose_name = "Изображение домика"
        verbose_name_plural = 'Изображения домиков'

    def __str__(self):
        return self.picture.name



class HouseFeature(models.Model):
    name = models.CharField("Название", max_length=127, unique=True)
    icon = models.ImageField("Иконка", upload_to=generate_house_feature_icon_filename)

    class Meta:
        verbose_name = "Фича домика"
        verbose_name_plural = 'Фичи домиков'

    def __str__(self):
        return self.name
