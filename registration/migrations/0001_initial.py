# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('name', models.CharField(max_length=200)),
                ('text', models.TextField()),
                ('imprint', models.TextField()),
                ('active', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Helper',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('prename', models.CharField(max_length=200)),
                ('surname', models.CharField(max_length=200)),
                ('email', models.EmailField(max_length=254)),
                ('phone', models.CharField(max_length=200)),
                ('comment', models.TextField()),
                ('shirt', models.CharField(choices=[('S', 'S'), ('M', 'M'), ('L', 'L'), ('XL', 'XL'), ('XXL', 'XXL'), ('S_GIRLY', 'S (girly)'), ('M_GIRLY', 'M (girly)'), ('L_GIRLY', 'L (girly)'), ('XL_GIRLY', 'XL (girly)')], max_length=20, default='S')),
            ],
        ),
        migrations.CreateModel(
            name='Job',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('name', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('event', models.ForeignKey(to='registration.Event')),
            ],
        ),
        migrations.CreateModel(
            name='Shift',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('begin', models.DateTimeField()),
                ('end', models.DateTimeField()),
                ('number', models.IntegerField(default=0)),
                ('job', models.ForeignKey(to='registration.Job')),
            ],
        ),
        migrations.AddField(
            model_name='helper',
            name='shifts',
            field=models.ManyToManyField(to='registration.Shift'),
        ),
    ]
