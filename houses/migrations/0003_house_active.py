# Generated by Django 5.0.3 on 2024-08-18 18:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('houses', '0002_rename_icon_housefeature_picture'),
    ]

    operations = [
        migrations.AddField(
            model_name='house',
            name='active',
            field=models.BooleanField(default=True, verbose_name='Домик в эксплуатации'),
        ),
    ]
