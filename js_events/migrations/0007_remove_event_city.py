# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-03-06 12:06
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('js_events', '0006_event_city'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='event',
            name='city',
        ),
    ]