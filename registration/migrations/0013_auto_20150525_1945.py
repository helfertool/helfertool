# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('registration', '0012_event_admins'),
    ]

    operations = [
        migrations.AddField(
            model_name='helper',
            name='infection_instruction',
            field=models.CharField(max_length=20, blank=True, choices=[('No', 'Einweisung noch nie erhalten'), ('Yes', 'Einweisung gültig'), ('Refresh', 'Ersteinweisung durch Arzt erhalten, Auffrischung nötig')]),
        ),
        migrations.AddField(
            model_name='job',
            name='infection_instruction',
            field=models.BooleanField(default=False),
        ),
    ]
