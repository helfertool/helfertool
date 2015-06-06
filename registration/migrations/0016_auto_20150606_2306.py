# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('registration', '0015_event_show_public_numbers'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='imprint_de',
            field=models.TextField(verbose_name='Imprint', help_text='Display at the bottom of the registration form.', blank=True, null=True),
        ),
        migrations.AddField(
            model_name='event',
            name='imprint_en',
            field=models.TextField(verbose_name='Imprint', help_text='Display at the bottom of the registration form.', blank=True, null=True),
        ),
        migrations.AddField(
            model_name='event',
            name='registered_de',
            field=models.TextField(verbose_name='Text after registration', help_text='Displayed after registration.', blank=True, null=True),
        ),
        migrations.AddField(
            model_name='event',
            name='registered_en',
            field=models.TextField(verbose_name='Text after registration', help_text='Displayed after registration.', blank=True, null=True),
        ),
        migrations.AddField(
            model_name='event',
            name='text_de',
            field=models.TextField(verbose_name='Text before registration', help_text='Displayed as first text of the registration form.', blank=True, null=True),
        ),
        migrations.AddField(
            model_name='event',
            name='text_en',
            field=models.TextField(verbose_name='Text before registration', help_text='Displayed as first text of the registration form.', blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='event',
            name='active',
            field=models.BooleanField(verbose_name='Registration possible', default=False),
        ),
        migrations.AlterField(
            model_name='event',
            name='ask_shirt',
            field=models.BooleanField(verbose_name='Ask for T-shirt size', default=True),
        ),
        migrations.AlterField(
            model_name='event',
            name='ask_vegetarian',
            field=models.BooleanField(verbose_name='Ask, if helper is vegetarian', default=True),
        ),
        migrations.AlterField(
            model_name='event',
            name='email',
            field=models.EmailField(max_length=254, default='party@fs.tum.de', verbose_name='E-Mail', help_text='Used as sender of e-mails.'),
        ),
        migrations.AlterField(
            model_name='event',
            name='imprint',
            field=models.TextField(verbose_name='Imprint', help_text='Display at the bottom of the registration form.', blank=True),
        ),
        migrations.AlterField(
            model_name='event',
            name='name',
            field=models.CharField(max_length=200, verbose_name='Event name'),
        ),
        migrations.AlterField(
            model_name='event',
            name='registered',
            field=models.TextField(verbose_name='Text after registration', help_text='Displayed after registration.', blank=True),
        ),
        migrations.AlterField(
            model_name='event',
            name='show_public_numbers',
            field=models.BooleanField(verbose_name='Show number of helpers on registration page', default=True),
        ),
        migrations.AlterField(
            model_name='event',
            name='text',
            field=models.TextField(verbose_name='Text before registration', help_text='Displayed as first text of the registration form.', blank=True),
        ),
        migrations.AlterField(
            model_name='event',
            name='url_name',
            field=models.CharField(max_length=200, unique=True, verbose_name='Name for URL', help_text='May contain the following chars: a-zA-Z0-9.', validators=[django.core.validators.RegexValidator('^[a-zA-Z0-9]+$')]),
        ),
    ]
