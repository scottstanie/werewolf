# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-04-19 19:55
from __future__ import unicode_literals

import django.contrib.postgres.fields
from django.db import migrations, models
import werewolf.models


class Migration(migrations.Migration):

    dependencies = [
        ('werewolf', '0002_auto_20160419_1440'),
    ]

    operations = [
        migrations.AddField(
            model_name='game',
            name='present',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=10), null=True, size=None),
        ),
        migrations.AlterField(
            model_name='game',
            name='name',
            field=models.CharField(default=werewolf.models._new_haiku, max_length=30, unique=True),
        ),
    ]
