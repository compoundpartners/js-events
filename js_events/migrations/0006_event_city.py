# -*- coding: utf-8 -*-
# Generated by Django 1.11.18 on 2019-02-21 05:41
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('js_events', '0005_auto_20190218_0714'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='city',
            field=models.CharField(blank=True, choices=[('Berlin', 'Berlin'), ('Copenhagen', 'Copenhagen'), ('Dusseldorf', 'Dusseldorf'), ('London', 'London'), ('Milan', 'Milan'), ('New York', 'New York'), ('Stockhol', 'Stockhol'), ('Vienna', 'Vienna'), ('Zurich', 'Zurich')], max_length=255, null=True, verbose_name='City'),
        ),
    ]