# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import uuid
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('registration', '0006_event_registered'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='url_name',
            field=models.CharField(unique=True, validators=[django.core.validators.RegexValidator('^[a-zA-Z0-9]+$')], max_length=200),
        ),
        migrations.AlterField(
            model_name='helper',
            name='id',
            field=models.UUIDField(editable=False, serialize=False, default=uuid.uuid4, primary_key=True),
        ),
    ]
