# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.core.validators
import django_bleach.models
from django.conf import settings
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('badges', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('url_name', models.CharField(unique=True, validators=[django.core.validators.RegexValidator('^[a-zA-Z0-9]+$')], max_length=200, help_text='May contain the following chars: a-zA-Z0-9.', verbose_name='Name for URL')),
                ('name', models.CharField(max_length=200, verbose_name='Event name')),
                ('text', django_bleach.models.BleachField(blank=True, help_text='Displayed as first text of the registration form.', verbose_name='Text before registration')),
                ('text_de', django_bleach.models.BleachField(null=True, blank=True, help_text='Displayed as first text of the registration form.', verbose_name='Text before registration')),
                ('text_en', django_bleach.models.BleachField(null=True, blank=True, help_text='Displayed as first text of the registration form.', verbose_name='Text before registration')),
                ('imprint', django_bleach.models.BleachField(blank=True, help_text='Display at the bottom of the registration form.', verbose_name='Imprint')),
                ('imprint_de', django_bleach.models.BleachField(null=True, blank=True, help_text='Display at the bottom of the registration form.', verbose_name='Imprint')),
                ('imprint_en', django_bleach.models.BleachField(null=True, blank=True, help_text='Display at the bottom of the registration form.', verbose_name='Imprint')),
                ('registered', django_bleach.models.BleachField(blank=True, help_text='Displayed after registration.', verbose_name='Text after registration')),
                ('registered_de', django_bleach.models.BleachField(null=True, blank=True, help_text='Displayed after registration.', verbose_name='Text after registration')),
                ('registered_en', django_bleach.models.BleachField(null=True, blank=True, help_text='Displayed after registration.', verbose_name='Text after registration')),
                ('email', models.EmailField(default='party@fs.tum.de', max_length=254, help_text='Used as sender of e-mails.', verbose_name='E-Mail')),
                ('logo', models.ImageField(null=True, upload_to='logos', blank=True, verbose_name='Logo')),
                ('max_overlapping', models.IntegerField(null=True, blank=True, help_text='If two shifts overlap more than this value in minutes it is not possible to register for both shifts. Leave empty to disable this check.', verbose_name='Maximal overlapping of shifts')),
                ('active', models.BooleanField(default=False, verbose_name='Registration possible')),
                ('ask_shirt', models.BooleanField(default=True, verbose_name='Ask for T-shirt size')),
                ('ask_vegetarian', models.BooleanField(default=True, verbose_name='Ask, if helper is vegetarian')),
                ('ask_full_age', models.BooleanField(default=True, verbose_name='Helpers have to confirm to be full age')),
                ('show_public_numbers', models.BooleanField(default=True, verbose_name='Show number of helpers on registration page')),
                ('mail_validation', models.BooleanField(default=True, verbose_name='Registrations for public shifts must be validated by a link that is sent per mail')),
                ('badges', models.BooleanField(default=False, verbose_name='Use badge creation')),
                ('admins', models.ManyToManyField(blank=True, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['name', 'url_name'],
            },
        ),
        migrations.CreateModel(
            name='Helper',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, serialize=False, primary_key=True, editable=False)),
                ('firstname', models.CharField(max_length=200, verbose_name='First name')),
                ('surname', models.CharField(max_length=200, verbose_name='Surname')),
                ('email', models.EmailField(max_length=254, verbose_name='E-Mail')),
                ('phone', models.CharField(max_length=200, verbose_name='Mobile phone')),
                ('comment', models.CharField(max_length=200, blank=True, verbose_name='Comment')),
                ('shirt', models.CharField(choices=[('S', 'S'), ('M', 'M'), ('L', 'L'), ('XL', 'XL'), ('XXL', 'XXL'), ('S_GIRLY', 'S (girly)'), ('M_GIRLY', 'M (girly)'), ('L_GIRLY', 'L (girly)'), ('XL_GIRLY', 'XL (girly)')], default='S', max_length=20, verbose_name='T-shirt')),
                ('vegetarian', models.BooleanField(default=False, help_text='This helps us estimating the food for our helpers.', verbose_name='Vegetarian')),
                ('infection_instruction', models.CharField(choices=[('No', 'I never got an instruction'), ('Yes', 'I have a valid instruction'), ('Refresh', 'I got a instruction by a doctor, it must be refreshed')], max_length=20, blank=True, verbose_name='Instruction for the handling of food')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('validated', models.BooleanField(default=True, verbose_name='E-Mail address was confirmed')),
                ('event', models.ForeignKey(to='registration.Event')),
            ],
        ),
        migrations.CreateModel(
            name='Job',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='Name')),
                ('name_de', models.CharField(null=True, max_length=200, verbose_name='Name')),
                ('name_en', models.CharField(null=True, max_length=200, verbose_name='Name')),
                ('public', models.BooleanField(default=False, verbose_name='This job is visible publicly')),
                ('infection_instruction', models.BooleanField(default=False, verbose_name='Instruction for the handling of food necessary')),
                ('description', django_bleach.models.BleachField(blank=True, verbose_name='Description')),
                ('description_de', django_bleach.models.BleachField(null=True, blank=True, verbose_name='Description')),
                ('description_en', django_bleach.models.BleachField(null=True, blank=True, verbose_name='Description')),
                ('badge_defaults', models.OneToOneField(null=True, to='badges.BadgeDefaults', blank=True)),
                ('coordinators', models.ManyToManyField(blank=True, to='registration.Helper')),
                ('event', models.ForeignKey(to='registration.Event')),
                ('job_admins', models.ManyToManyField(blank=True, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Link',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, serialize=False, primary_key=True, editable=False)),
                ('usage', models.CharField(max_length=200, blank=True, verbose_name='Usage')),
                ('creator', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('event', models.ForeignKey(to='registration.Event')),
            ],
        ),
        migrations.CreateModel(
            name='Shift',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('name', models.CharField(default='', max_length=200, blank=True, verbose_name='Name (optional)')),
                ('begin', models.DateTimeField(verbose_name='Begin')),
                ('end', models.DateTimeField(verbose_name='End')),
                ('number', models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0)], verbose_name='Number of helpers')),
                ('blocked', models.BooleanField(default=False, verbose_name='If the job is publicly visible, the shift is blocked.')),
                ('job', models.ForeignKey(to='registration.Job')),
            ],
            options={
                'ordering': ['job', 'begin', 'end'],
            },
        ),
        migrations.AddField(
            model_name='link',
            name='shifts',
            field=models.ManyToManyField(to='registration.Shift'),
        ),
        migrations.AddField(
            model_name='helper',
            name='shifts',
            field=models.ManyToManyField(to='registration.Shift'),
        ),
    ]
