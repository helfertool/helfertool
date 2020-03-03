# Generated by Django 2.2.10 on 2020-02-27 14:34

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gifts', '0008_auto_20170401_1512'),
    ]

    operations = [
        migrations.AlterField(
            model_name='includedgift',
            name='count',
            field=models.FloatField(default=1, validators=[django.core.validators.MinValueValidator(1)], verbose_name='Count'),
        ),
    ]