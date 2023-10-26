from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.db import models


class Event(models.Model):
    name = models.CharField("Название события", max_length=127)

    start_date = models.DateField("Дата начала события")
    end_date = models.DateField("Дата конца события")

    multiplier = models.FloatField("Множитель события", default=1)

    created_at = models.DateTimeField("Время создания события", auto_now_add=True)
    updated_at = models.DateTimeField("Время последнего изменения события", auto_now=True)

    class Meta:
        verbose_name = "Событие"
        verbose_name_plural = 'События'

    def clear_event_cache(self):
        # TODO
        cache.clear()

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def clean(self, *args, **kwargs):
        if self.start_date > self.end_date:
            raise ValidationError("Дата начала события не должна быть больше даты окончания события")

        if self.multiplier < 1:
            raise ValidationError("Если вы реально хотите устроить сезон скидок и поставить "
                                  "уменьшение цены - обратитесь к разработчику")

    def __str__(self):
        return f'{self.name} {self.start_date.strftime("%d.%m")}-{self.end_date.strftime("%d.%m")}'
