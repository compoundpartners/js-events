# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-05-24 10:04
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('js_events', '0014_speaker_function'),
    ]

    operations = [
        migrations.AddField(
            model_name='speaker',
            name='vcard_enabled',
            field=models.BooleanField(default=True, verbose_name='enable vCard download'),
        ),
    ]
