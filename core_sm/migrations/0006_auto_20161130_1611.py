# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-11-30 16:11
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core_sm', '0005_auto_20161130_1554'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='budget',
            options={'ordering': ('-start_date',)},
        ),
    ]
