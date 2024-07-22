import logging

from django.db import models

from additional_services.filepath_generators import generate_additional_service_picture_filename

logger = logging.getLogger(__name__)


class AdditionalService(models.Model):
    name = models.CharField("Название услуги", max_length=255, unique=True)

    active = models.BooleanField("Услуга актуальна", default=True)

    description = models.TextField("Описание услуги")

    telegram_contact_link = models.CharField("Ссылка на телеграм для бронирования", max_length=127)
    price_string = models.CharField("Стоимость услуги", max_length=15)

    created_at = models.DateTimeField("Время создания услуги", auto_now_add=True)
    updated_at = models.DateTimeField("Время последнего изменения услуги", auto_now=True)

    class Meta:
        verbose_name = "Услуга"
        verbose_name_plural = 'Услуги'

    def __str__(self):
        return f"({self.id}) {self.name}"


class AdditionalServicePicture(models.Model):
    additional_service = models.ForeignKey(AdditionalService, verbose_name="Услуга",
                                           on_delete=models.SET_NULL,
                                           null=True, related_name='pictures')
    picture = models.ImageField("Путь до файла с изображением",
                                upload_to=generate_additional_service_picture_filename)

    class Meta:
        verbose_name = "Изображение услуги"
        verbose_name_plural = 'Изображения услуг'

    def __str__(self):
        return self.picture.name
