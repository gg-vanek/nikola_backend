from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models

name_validator = RegexValidator(regex="^[0-9a-zA-Zа-яА-Я ,.'-_]+$",
                                message='Имя и фамилия должны состоять из только из цифр, "\
                                        "строчных и заглавных букв русского "\
                                        "и английского алфавитов, пробелов, а также из символов ",.\'-_")')


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
            raise ValidationError("First name can not be a blank string", code="invalid")
        if self.last_name == "":
            raise ValidationError("Last name can not be a blank string", code="invalid")

    def __str__(self):
        return self.email
