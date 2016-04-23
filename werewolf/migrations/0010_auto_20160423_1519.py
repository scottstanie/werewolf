# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-04-23 15:19
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('werewolf', '0009_auto_20160423_1236'),
    ]

    operations = [
        migrations.AlterField(
            model_name='game',
            name='created_date',
            field=models.DateTimeField(auto_now_add=True, verbose_name=b'date created'),
        ),
        migrations.AlterField(
            model_name='matchup',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]