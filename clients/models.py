from django.core.exceptions import ModelValidationError
from django.db import models

from core.validators import name_validator


class Client(models.Model):
    email = models.EmailField("Email адрес", unique=True)

    first_name = models.CharField("Имя", validators=[name_validator], max_length=150, blank=True)
    last_name = models.CharField("Фамилия", validators=[name_validator], max_length=150, blank=True)

    created_at = models.DateTimeField("Время создания клиента", auto_now_add=True)
    updated_at = models.DateTimeField("Время последнего изменения клиента", auto_now=True)

    class Meta:
        verbose_name = "Клиент"
        verbose_name_plural = "Клиенты"

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def clean(self, *args, **kwargs):
        self.first_name = self.first_name.strip()
        self.last_name = self.last_name.strip()

        if self.first_name == "":
            raise ModelValidationError("First name can not be a blank string", code="invalid")
        if self.last_name == "":
            raise ModelValidationError("Last name can not be a blank string", code="invalid")

    def __str__(self):
        return self.email
