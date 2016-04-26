# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-04-26 02:42
from __future__ import unicode_literals

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('werewolf', '0019_game_winning_team'),
    ]

    operations = [
        migrations.AlterField(
            model_name='game',
            name='winning_team',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(choices=[(b'villager', b'Villager Team'), (b'werewolf', b'Werewolf Team'), (b'tanner', b'Tanner Team')], max_length=30), default=[], size=None),
        ),
    ]
