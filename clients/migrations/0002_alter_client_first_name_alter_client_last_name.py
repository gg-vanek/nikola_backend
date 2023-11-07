# Generated by Django 4.2.6 on 2023-10-18 21:11

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clients', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='client',
            name='first_name',
            field=models.CharField(blank=True, max_length=150, validators=[django.core.validators.RegexValidator(message='Имя и фамилия должны состоять из только из цифр, "                                        "строчных и заглавных букв русского "                                        "и английского алфавитов, пробелов, а также из символов ",.\'-_")', regex="^[0-9a-zA-Zа-яА-Я ,.'-_]+$")], verbose_name='Имя'),
        ),
        migrations.AlterField(
            model_name='client',
            name='last_name',
            field=models.CharField(blank=True, max_length=150, validators=[django.core.validators.RegexValidator(message='Имя и фамилия должны состоять из только из цифр, "                                        "строчных и заглавных букв русского "                                        "и английского алфавитов, пробелов, а также из символов ",.\'-_")', regex="^[0-9a-zA-Zа-яА-Я ,.'-_]+$")], verbose_name='Фамилия'),
        ),
    ]
