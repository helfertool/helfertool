# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django_bleach.models
from django.conf import settings
import django.core.validators
import uuid


class Migration(migrations.Migration):

    replaces = [('registration', '0001_initial'), ('registration', '0002_badge_primary_job'), ('registration', '0003_auto_20150928_0007'), ('registration', '0004_auto_20150928_0007'), ('registration', '0005_helper_event'), ('registration', '0006_event_logo'), ('registration', '0007_event_max_overlapping'), ('registration', '0008_auto_20151003_1323'), ('registration', '0009_auto_20151003_1325'), ('registration', '0010_auto_20151017_1504'), ('registration', '0011_auto_20151018_1310'), ('registration', '0012_auto_20151018_1946'), ('registration', '0013_badgesettings_barcodes'), ('registration', '0014_badge_printed'), ('registration', '0015_auto_20151101_1306'), ('registration', '0016_shift_name'), ('registration', '0017_auto_20151114_1505'), ('registration', '0018_auto_20151114_1508'), ('registration', '0019_auto_20151114_1851'), ('registration', '0020_auto_20151114_1854'), ('registration', '0021_auto_20151220_1857'), ('registration', '0022_auto_20151220_1900'), ('registration', '0023_remove_helper_full_age'), ('registration', '0024_auto_20151220_1920'), ('registration', '0025_auto_20151229_1504'), ('registration', '0026_auto_20151229_1743')]

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='BadgeDefaults',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
            ],
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('url_name', models.CharField(unique=True, verbose_name='Name for URL', help_text='May contain the following chars: a-zA-Z0-9.', max_length=200, validators=[django.core.validators.RegexValidator('^[a-zA-Z0-9]+$')])),
                ('name', models.CharField(verbose_name='Event name', max_length=200)),
                ('text', models.TextField(blank=True, verbose_name='Text before registration', help_text='Displayed as first text of the registration form.')),
                ('text_de', models.TextField(verbose_name='Text before registration', blank=True, null=True, help_text='Displayed as first text of the registration form.')),
                ('text_en', models.TextField(verbose_name='Text before registration', blank=True, null=True, help_text='Displayed as first text of the registration form.')),
                ('imprint', models.TextField(blank=True, verbose_name='Imprint', help_text='Display at the bottom of the registration form.')),
                ('imprint_de', models.TextField(verbose_name='Imprint', blank=True, null=True, help_text='Display at the bottom of the registration form.')),
                ('imprint_en', models.TextField(verbose_name='Imprint', blank=True, null=True, help_text='Display at the bottom of the registration form.')),
                ('registered', models.TextField(blank=True, verbose_name='Text after registration', help_text='Displayed after registration.')),
                ('registered_de', models.TextField(verbose_name='Text after registration', blank=True, null=True, help_text='Displayed after registration.')),
                ('registered_en', models.TextField(verbose_name='Text after registration', blank=True, null=True, help_text='Displayed after registration.')),
                ('email', models.EmailField(default='party@fs.tum.de', verbose_name='E-Mail', help_text='Used as sender of e-mails.', max_length=254)),
                ('active', models.BooleanField(default=False, verbose_name='Registration possible')),
                ('ask_shirt', models.BooleanField(default=True, verbose_name='Ask for T-shirt size')),
                ('ask_vegetarian', models.BooleanField(default=True, verbose_name='Ask, if helper is vegetarian')),
                ('show_public_numbers', models.BooleanField(default=True, verbose_name='Show number of helpers on registration page')),
                ('mail_validation', models.BooleanField(default=True, verbose_name='Registrations for public shifts must be validated by a link that is sent per mail')),
                ('badges', models.BooleanField(default=False, verbose_name='Use badge creation')),
                ('admins', models.ManyToManyField(blank=True, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Helper',
            fields=[
                ('id', models.UUIDField(primary_key=True, default=uuid.uuid4, serialize=False, editable=False)),
                ('prename', models.CharField(verbose_name='Prename', max_length=200)),
                ('surname', models.CharField(verbose_name='Surname', max_length=200)),
                ('email', models.EmailField(verbose_name='E-Mail', max_length=254)),
                ('phone', models.CharField(verbose_name='Mobile phone', max_length=200)),
                ('comment', models.CharField(blank=True, verbose_name='Comment', max_length=200)),
                ('shirt', models.CharField(default='S', verbose_name='T-shirt', max_length=20, choices=[('S', 'S'), ('M', 'M'), ('L', 'L'), ('XL', 'XL'), ('XXL', 'XXL'), ('S_GIRLY', 'S (girly)'), ('M_GIRLY', 'M (girly)'), ('L_GIRLY', 'L (girly)'), ('XL_GIRLY', 'XL (girly)')])),
                ('vegetarian', models.BooleanField(default=False, verbose_name='Vegetarian', help_text='This helps us estimating the food for our helpers.')),
                ('infection_instruction', models.CharField(blank=True, verbose_name='Instruction for the handling of food', max_length=20, choices=[('No', 'I never got an instruction'), ('Yes', 'I have a valid instruction'), ('Refresh', 'I got a instruction by a doctor, it must be refreshed')])),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('validated', models.BooleanField(default=True, verbose_name='E-Mail address was confirmed')),
            ],
        ),
        migrations.CreateModel(
            name='Job',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('name', models.CharField(verbose_name='Name', max_length=200)),
                ('name_de', models.CharField(verbose_name='Name', null=True, max_length=200)),
                ('name_en', models.CharField(verbose_name='Name', null=True, max_length=200)),
                ('public', models.BooleanField(default=False, verbose_name='This job is visible publicly')),
                ('infection_instruction', models.BooleanField(default=False, verbose_name='Instruction for the handling of food necessary')),
                ('description', models.TextField(blank=True, verbose_name='Description')),
                ('description_de', models.TextField(verbose_name='Description', blank=True, null=True)),
                ('description_en', models.TextField(verbose_name='Description', blank=True, null=True)),
                ('badge_defaults', models.OneToOneField(blank=True, null=True, to='registration.BadgeDefaults')),
                ('coordinators', models.ManyToManyField(blank=True, to='registration.Helper')),
                ('event', models.ForeignKey(to='registration.Event')),
                ('job_admins', models.ManyToManyField(blank=True, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Link',
            fields=[
                ('id', models.UUIDField(primary_key=True, default=uuid.uuid4, serialize=False, editable=False)),
                ('usage', models.CharField(blank=True, verbose_name='Usage', max_length=200)),
                ('creator', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('event', models.ForeignKey(to='registration.Event')),
            ],
        ),
        migrations.CreateModel(
            name='Shift',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('begin', models.DateTimeField(verbose_name='Begin')),
                ('end', models.DateTimeField(verbose_name='End')),
                ('number', models.IntegerField(default=0, verbose_name='Number of helpers', validators=[django.core.validators.MinValueValidator(0)])),
                ('blocked', models.BooleanField(default=False, verbose_name='If the job is publicly visible, the shift is blocked.')),
                ('job', models.ForeignKey(to='registration.Job')),
                ('name', models.CharField(default='', verbose_name='Name (optional)', max_length=200, blank=True)),
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
        migrations.AddField(
            model_name='helper',
            name='event',
            field=models.ForeignKey(default=None, to='registration.Event'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='event',
            name='logo',
            field=models.ImageField(verbose_name='Logo', blank=True, null=True, upload_to='logos'),
        ),
        migrations.AddField(
            model_name='event',
            name='max_overlapping',
            field=models.IntegerField(verbose_name='Maximal overlapping of shifts', blank=True, null=True, help_text='If two shifts overlap more than this value in minutes it is not possible to register for both shifts. Leave empty to disable this check.'),
        ),
        migrations.AlterModelOptions(
            name='event',
            options={'ordering': ['name', 'url_name']},
        ),
        migrations.RenameField(
            model_name='helper',
            old_name='prename',
            new_name='firstname',
        ),
        migrations.AlterField(
            model_name='helper',
            name='firstname',
            field=models.CharField(verbose_name='First name', max_length=200),
        ),
        migrations.AlterField(
            model_name='event',
            name='text',
            field=django_bleach.models.BleachField(blank=True, verbose_name='Text before registration', help_text='Displayed as first text of the registration form.'),
        ),
        migrations.AlterField(
            model_name='event',
            name='text_de',
            field=django_bleach.models.BleachField(verbose_name='Text before registration', blank=True, null=True, help_text='Displayed as first text of the registration form.'),
        ),
        migrations.AlterField(
            model_name='event',
            name='text_en',
            field=django_bleach.models.BleachField(verbose_name='Text before registration', blank=True, null=True, help_text='Displayed as first text of the registration form.'),
        ),
        migrations.AlterField(
            model_name='event',
            name='imprint',
            field=django_bleach.models.BleachField(blank=True, verbose_name='Imprint', help_text='Display at the bottom of the registration form.'),
        ),
        migrations.AlterField(
            model_name='event',
            name='imprint_de',
            field=django_bleach.models.BleachField(verbose_name='Imprint', blank=True, null=True, help_text='Display at the bottom of the registration form.'),
        ),
        migrations.AlterField(
            model_name='event',
            name='imprint_en',
            field=django_bleach.models.BleachField(verbose_name='Imprint', blank=True, null=True, help_text='Display at the bottom of the registration form.'),
        ),
        migrations.AlterField(
            model_name='event',
            name='registered',
            field=django_bleach.models.BleachField(blank=True, verbose_name='Text after registration', help_text='Displayed after registration.'),
        ),
        migrations.AlterField(
            model_name='event',
            name='registered_de',
            field=django_bleach.models.BleachField(verbose_name='Text after registration', blank=True, null=True, help_text='Displayed after registration.'),
        ),
        migrations.AlterField(
            model_name='event',
            name='registered_en',
            field=django_bleach.models.BleachField(verbose_name='Text after registration', blank=True, null=True, help_text='Displayed after registration.'),
        ),
        migrations.AlterField(
            model_name='job',
            name='description',
            field=django_bleach.models.BleachField(blank=True, verbose_name='Description'),
        ),
        migrations.AlterField(
            model_name='job',
            name='description_de',
            field=django_bleach.models.BleachField(verbose_name='Description', blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='job',
            name='description_en',
            field=django_bleach.models.BleachField(verbose_name='Description', blank=True, null=True),
        ),
        migrations.AddField(
            model_name='event',
            name='ask_full_age',
            field=models.BooleanField(default=True, verbose_name='Helpers have to confirm to be full age'),
        ),
        migrations.AlterField(
            model_name='job',
            name='badge_defaults',
            field=models.OneToOneField(blank=True, null=True, to='badges.BadgeDefaults'),
        ),
        migrations.DeleteModel(
            name='BadgeDefaults',
        ),
    ]
