# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-11-18 06:32
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('testapp', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='test',
            name='system_status',
            field=models.BooleanField(default=False),
        ),
    ]