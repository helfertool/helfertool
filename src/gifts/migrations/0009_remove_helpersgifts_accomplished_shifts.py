# Generated by Django 2.2.10 on 2020-03-11 19:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gifts', '0008_auto_20170401_1512'),
        ('registration', '0033_migrate_shiftattendance'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='helpersgifts',
            name='accomplished_shifts',
        ),
    ]