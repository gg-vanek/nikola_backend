# Generated by Django 5.0.3 on 2024-08-18 18:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('additional_services', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='additionalservice',
            name='active',
            field=models.BooleanField(default=True, verbose_name='Услуга актуальна'),
        ),
    ]
