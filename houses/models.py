import os
from django.core.validators import MinValueValidator
from django.db import models


def generate_house_picture_filename(instance, filename):
    path = os.path.join('houses', 'pictures', str(instance.house.id), filename)
    return path


class House(models.Model):
    MIN_BASE_PRICE = 1000
    MIN_HOLIDAYS_MULTIPLIER = 1

    name = models.CharField("Название домика", max_length=255, unique=True)
    description = models.TextField("Описание домика")

    base_price = models.IntegerField(
        "Базовая цена",
        validators=[
            MinValueValidator(MIN_BASE_PRICE,
                              message=f"Базовая цена домика должна быть не меньше, чем {MIN_BASE_PRICE}"),
        ])
    holidays_multiplier = models.FloatField(
        "Множитель в выходные и праздники",
        default=1,
        validators=[
            MinValueValidator(MIN_HOLIDAYS_MULTIPLIER,
                              message=f"Множитель в выходные дни должен быть не меньше, чем {MIN_HOLIDAYS_MULTIPLIER}"),
        ])

    created_at = models.DateTimeField("Время создания домика", auto_now_add=True)
    updated_at = models.DateTimeField("Время последнего изменения домика", auto_now=True)

    class Meta:
        verbose_name = "Домик"
        verbose_name_plural = 'Домики'

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class HousePicture(models.Model):
    house = models.ForeignKey(House, on_delete=models.SET_NULL, null=True, related_name='pictures')
    picture = models.ImageField(upload_to=generate_house_picture_filename)

    class Meta:
        verbose_name = "Изображение домика"
        verbose_name_plural = 'Изображения домиков'

    def __str__(self):
        return self.picture.name
